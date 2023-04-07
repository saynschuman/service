from openpyxl import load_workbook
from rest_framework import serializers

from backend.constants import QUESTIONS_CREATE, TASK_ID_ERROR, PARSE_ERROR, DB_ERROR
from backend.courses.models import Question, Task, Answer
from backend.users.utils import file_validator


class QuestionSerializer(serializers.ModelSerializer):
    """
    Сериализатор вопросов для таска
    """

    class Meta:
        model = Question
        fields = '__all__'


class QuestionFileSerializer(serializers.Serializer):
    """
    Сериализатор вопросов для таска из файла '.xlsx'
    """

    file = serializers.FileField(
        label='Файл со списком вопросов/ответов',
        validators=[file_validator],
    )
    task = serializers.IntegerField(
        label='ID задания',
    )

    @staticmethod
    def create_questions(validated_data, question_file):
        status = True
        result_list = []
        code = QUESTIONS_CREATE
        message = 'Вопросы успешно созданы'

        # Проверка есть ли такой таск
        task_id = validated_data.get('task')
        try:
            Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            status = False
            code = TASK_ID_ERROR
            message = f'Для id_{task_id} не удалось найти объекта задания'
            return status, message, result_list, code

        # Парсим файл
        try:
            wb = load_workbook(filename=question_file)
            sheet = wb.active
            num_questions_col = sheet['A']
            score_col = sheet['B']
            text_col = sheet['C']
            answer_col = sheet['D']
            is_true_col = sheet['E']

            questions = []

            for cell in num_questions_col:
                # Пропускаем первую строку - названия сто
                if cell.row == 1:
                    continue

                if cell.value:
                    try:
                        questions[-1].append(cell.row - 1)
                    except IndexError:
                        # нет предыдущего значения
                        pass
                    questions.append([cell.row])

            for question in questions:
                # последний вопрос
                if len(question) == 1:
                    question.append(float('inf'))

                cx_start, cx_end = question[0], question[1]

                for cell in text_col:
                    if cell.row == cx_start:
                        question.append(cell.value)

                for cell in score_col:
                    if cell.row == cx_start:
                        question.append(cell.value)

                answers = []
                for cell in answer_col:
                    if cx_end >= cell.row >= cx_start and cell.value:
                        answers.append([cell.row, cell.value])

                for answer in answers:
                    for cell in is_true_col:
                        if cell.row == answer[0]:
                            answer.append(cell.value)

                question.append(answers)
        except:
            status = False
            code = PARSE_ERROR
            message = 'Ошибка разбора файла'
            return status, message, result_list, code

        # Создание вопросов
        try:
            for _, _, text, score, answers_list in questions:
                payload = {
                    'is_free_answer': True
                }
                if score:
                    payload['score'] = score
                if bool(answers_list):
                    payload['is_free_answer'] = False

                question_instance = Question.objects.create(
                    text=text,
                    **payload,
                )
                question_instance.tasks.add(task_id)
                result_list.append(question_instance)

                # Создание ответов
                for _, answer, is_true in answers_list:
                    Answer.objects.create(
                        question=question_instance,
                        text=answer,
                        is_true=bool(is_true),
                    )
        except Exception as ex:
            status = False
            code = DB_ERROR
            message = f'Ошибка базы данных во время создания объектов: {str(ex)}'
            return status, message, result_list, code

        return status, message, result_list, code
