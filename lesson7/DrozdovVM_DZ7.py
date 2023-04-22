"""Вот реализация класса CourtCase с указанными атрибутами и методами"""
class CourtCase:
    def __init__(self, case_number):
        self.case_number = case_number
        self.case_participants = []
        self.listening_datetimes = []
        self.is_finished = False
        self.verdict = ''

    def set_a_listening_datetime(self, datetime):
        self.listening_datetimes.append(datetime)

    def add_participant(self, participant):
        self.case_participants.append(participant)

    def remove_participant(self, participant):
        self.case_participants.remove(participant)

    def make_a_decision(self, verdict):
        self.verdict = verdict
        self.is_finished = True

"""Пример использования:"""
case = CourtCase('123/2022')
case.add_participant('1234567890')
case.set_a_listening_datetime('2023-05-01 14:00')
case.set_a_listening_datetime('2023-05-03 10:00')
case.remove_participant('1234567890')
case.make_a_decision('Обвиняемый признан виновным.')
print(case.verdict)  #'Обвиняемый признан виновным'
print(case.is_finished)  # True
