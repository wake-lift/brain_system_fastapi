from elastic_transport import ObjectApiResponse
from elasticsearch import (Elasticsearch, BadRequestError, helpers,
                           NotFoundError)
from sqlalchemy import desc, false, select, true

from app.core.config import settings
from app.core.db import sync_session_factory
from app.elasticsearch import dsl_queries as dsl
from app.models.questions import Question


class ElasticSerchBase():
    """Базовый класс для работы с индексом Elasticsearch."""

    def __init__(
            self,
            host: str = settings.elasticsearch_host,
            port: str = settings.elasticsearch_port,
            index: str = 'question_index'
    ) -> None:
        self.es_client: Elasticsearch = Elasticsearch(
            f'http://{host}:{port}',
            timeout=60,
            retry_on_timeout=True,
            max_retries=10
        )
        self.index: str = index

    def create_index(
            self,
            mapping: dict = dsl.QUESTION_INDEX_MAPPING,
            settings: dict = dsl.QUESTION_INDEX_SETTINGS
    ) -> dict | str:
        """Создание нового индекса."""
        try:
            idx = self.es_client.indices.create(
                index=self.index,
                mappings=mapping,
                settings=settings
            )
        except BadRequestError as error:
            print(f'При создании индекса возникла ошибка: {error.error}')
            return error.error
        print('Индекс успешно создан')
        return idx.body

    def delete_index(self) -> dict | str:
        """Удаление индекса."""
        try:
            idx = self.es_client.indices.delete(index=self.index)
        except (BadRequestError, NotFoundError) as err:
            print(f'При удаленн индекса возникла ошибка: {err.error}')
            return err.error
        print('Индекс успешно удален')
        return idx.body

    def remove_all_docs_from_index(self) -> None:
        """Удаление всех документов из индекса."""
        try:
            self.es_client.delete_by_query(
                index=self.index, body=dsl.GET_ALL_DOCS_IN_INDEX
            )
        except Exception as err:
            print(f'При удалении данных произошла ошибка: {err}.')


class ElasticSerchQuestion(ElasticSerchBase):
    """Класс для работы с индексом вопросов для интеллектуальных игр."""

    @staticmethod
    def __prepare_questions(right_idx: int, left_idx: int) -> list[dict]:
        """
        Выбирает из БД вопросы, соответствующие переданному диапазону первичных
        ключей, и приводит их в готовый для экспорта в индекс вид.
        """
        question_list = []
        with sync_session_factory() as session:
            questions = session.execute(
                select(Question.id, Question.question_type, Question.question)
                .filter(
                    Question.id.between(right_idx, left_idx),
                    Question.is_condemned == false(),
                    Question.is_published == true()
                )
            )
        for question in questions.all():
            question_list.append({
                'pk': question.id,
                'question_type': question.question_type.value,
                'question': question.question})
        return question_list

    def export_data_from_db_to_index(self) -> None:
        """
        Экспортирует содержимое БД в индекс в несколько итераций.
        """
        with sync_session_factory() as session:
            last_question_id = session.scalar(
                select(Question.id)
                .order_by(desc(Question.id))
                .limit(1)
            )
        upload_intervals = [_ for _ in range(1, last_question_id + 1, 10000)]
        upload_intervals.append(last_question_id)
        self.remove_all_docs_from_index()
        for i in range(len(upload_intervals) - 1):
            try:
                uploaded_questions = ElasticSerchQuestion.__prepare_questions(
                    upload_intervals[i], upload_intervals[i + 1]
                )
                helpers.bulk(
                    self.es_client, uploaded_questions, index=self.index
                )
            except Exception as err:
                self.remove_all_docs_from_index()
                print((f'При экспорте данных произошла ошибка: {err}.'
                       'Выполнена очистка индекса.'))
                break

    def search_questions(
            self,
            search_pattern: str,
            quantity: int,
            question_type: str = None
    ) -> ObjectApiResponse:
        """Поиск вопросов в индексе."""
        body = dsl.get_searh_query(search_pattern, question_type)
        return self.es_client.search(
            index=self.index, size=quantity, body=body
        )

    def get_questions_pk_list(
            self, search_result: ObjectApiResponse
    ) -> list[int]:
        """
        Возвращает список первичных ключей записей
        на основании результата поиска в индексе.
        """
        return [_['_source']['pk'] for _ in search_result.body['hits']['hits']]
