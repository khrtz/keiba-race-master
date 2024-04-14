import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, \
    QPushButton, QTextEdit, QTableWidget, QTableWidgetItem, QCheckBox, QComboBox, QDialog, QDialogButtonBox
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtCore import Qt
import re


class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("データソース編集")
        self.resize(600, 400)

        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def set_text(self, text):
        self.text_edit.setPlainText(text)

    def get_text(self):
        return self.text_edit.toPlainText()


class BettingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Race Master")
        self.setGeometry(100, 100, 800, 600)

        self.race_data = {}
        self.current_race = ""

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.create_race_input_layout()
        self.create_horse_table()
        self.create_bet_table()

        self.set_style()

    def create_race_input_layout(self):
        race_input_layout = QHBoxLayout()

        race_name_label = QLabel("レース名:")
        race_name_label.setFont(QFont("Arial", 12))
        self.race_name_input = QLineEdit()
        self.race_name_input.setFont(QFont("Arial", 12))
        race_input_layout.addWidget(race_name_label)
        race_input_layout.addWidget(self.race_name_input)

        race_date_label = QLabel("日付:")
        race_date_label.setFont(QFont("Arial", 12))
        self.race_date_input = QLineEdit()
        self.race_date_input.setFont(QFont("Arial", 12))
        race_input_layout.addWidget(race_date_label)
        race_input_layout.addWidget(self.race_date_input)

        self.save_button = QPushButton("保存")
        self.save_button.setFont(QFont("Arial", 12))
        self.save_button.clicked.connect(self.save_race)
        race_input_layout.addWidget(self.save_button)

        self.edit_button = QPushButton("編集")
        self.edit_button.setFont(QFont("Arial", 12))
        self.edit_button.clicked.connect(self.edit_data_source)
        race_input_layout.addWidget(self.edit_button)

        self.race_selector = QComboBox()
        self.race_selector.setFont(QFont("Arial", 12))
        self.race_selector.currentIndexChanged.connect(self.change_race)
        race_input_layout.addWidget(self.race_selector)

        self.layout.addLayout(race_input_layout)

    def create_horse_table(self):
        self.horse_table = QTableWidget()
        self.horse_table.setColumnCount(8)
        self.horse_table.setHorizontalHeaderLabels(["選択", "馬名", "性別", "年齢", "斤量", "騎手", "調教師", "オッズ"])
        self.horse_table.horizontalHeader().setFont(QFont("Arial", 12))
        self.horse_table.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.horse_table)

    def create_bet_table(self):
        self.bet_table = QTableWidget()
        self.bet_table.setColumnCount(7)
        self.bet_table.setHorizontalHeaderLabels(["馬券", "馬名1", "馬名2", "馬名3", "馬名4", "馬名5", "オッズ"])
        self.bet_table.horizontalHeader().setFont(QFont("Arial", 12))
        self.bet_table.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.bet_table)
    def save_race(self):
        race_name = self.race_name_input.text()
        race_date = self.race_date_input.text()
        horse_data = self.get_horse_data()

        self.race_data[race_name] = {
            "date": race_date,
            "horses": horse_data
        }

        self.current_race = race_name
        self.update_race_selector()
        self.display_horses()

    def edit_data_source(self):
        if self.current_race in self.race_data:
            dialog = InputDialog(self)
            data_source = self.race_data[self.current_race].get("data_source", "")
            dialog.set_text(data_source)

            if dialog.exec() == QDialog.Accepted:
                self.race_data[self.current_race]["data_source"] = dialog.get_text()
                horse_data = self.parse_horse_data(dialog.get_text())
                self.race_data[self.current_race]["horses"] = horse_data
                self.display_horses()

    def get_horse_data(self):
        horse_data = []
        for i in range(self.horse_table.rowCount()):
            horse = {
                "name": self.horse_table.item(i, 1).text(),
                "sex": self.horse_table.item(i, 2).text(),
                "age": self.horse_table.item(i, 3).text(),
                "weight": self.horse_table.item(i, 4).text(),
                "jockey": self.horse_table.item(i, 5).text(),
                "trainer": self.horse_table.item(i, 6).text(),
                "odds": self.horse_table.item(i, 7).text(),
                "selected": self.horse_table.cellWidget(i, 0).isChecked()
            }
            horse_data.append(horse)
        return horse_data

    def update_race_selector(self):
        self.race_selector.clear()
        self.race_selector.addItems(list(self.race_data.keys()))
        self.race_selector.setCurrentText(self.current_race)

    def change_race(self):
        self.current_race = self.race_selector.currentText()
        self.display_horses()

    def display_horses(self):
        if self.current_race in self.race_data:
            race_info = self.race_data[self.current_race]
            horses = race_info["horses"]
            self.horse_table.setRowCount(len(horses))
            for i, horse in enumerate(horses):
                checkbox = QCheckBox()
                checkbox.setChecked(horse.get("selected", False))
                checkbox.stateChanged.connect(self.update_bets)
                self.horse_table.setCellWidget(i, 0, checkbox)
                self.horse_table.setItem(i, 1, QTableWidgetItem(horse["name"]))
                self.horse_table.setItem(i, 2, QTableWidgetItem(horse["sex"]))
                self.horse_table.setItem(i, 3, QTableWidgetItem(horse["age"]))
                self.horse_table.setItem(i, 4, QTableWidgetItem(horse["weight"]))
                self.horse_table.setItem(i, 5, QTableWidgetItem(horse["jockey"]))
                self.horse_table.setItem(i, 6, QTableWidgetItem(horse["trainer"]))
                odds_item = QTableWidgetItem(horse["odds"] if "odds" in horse else "")
                self.horse_table.setItem(i, 7, odds_item)
        else:
            self.horse_table.setRowCount(0)

        self.update_bets()

    def update_bets(self):
        selected_horses = []
        for i in range(self.horse_table.rowCount()):
            checkbox = self.horse_table.cellWidget(i, 0)
            if checkbox.isChecked():
                horse_name = self.horse_table.item(i, 1).text()
                odds_item = self.horse_table.item(i, 7)
                horse_odds = float(odds_item.text()) if odds_item and odds_item.text() else 0.0
                if horse_odds > 0:
                    selected_horses.append((horse_name, horse_odds))

        self.display_bets(selected_horses)

    def display_bets(self, selected_horses):
        self.bet_table.clearContents()
        self.bet_table.setRowCount(0)

        # 単勝ベットの表示
        if len(selected_horses) >= 1:
            for horse, odds in selected_horses:
                # 単勝の場合は馬名1つのみ、その他は空文字
                self.add_bet_row("単勝", horse, "", "", "", "", odds)

        # 馬連ベットの表示
        if len(selected_horses) >= 2:
            for i in range(len(selected_horses) - 1):
                for j in range(i + 1, len(selected_horses)):
                    horse1, odds1 = selected_horses[i]
                    horse2, odds2 = selected_horses[j]
                    self.add_bet_row("馬連", horse1, horse2, "", "", "", odds1 * odds2)

        # 馬単ベットの表示
        if len(selected_horses) >= 2:
            for i in range(len(selected_horses)):
                for j in range(len(selected_horses)):
                    if i != j:
                        horse1, odds1 = selected_horses[i]
                        horse2, odds2 = selected_horses[j]
                        self.add_bet_row("馬単", horse1, horse2, "", "", "", odds1 * odds2)

        # 3連複ベットの表示
        if len(selected_horses) >= 3:
            from itertools import combinations
            for combo in combinations(selected_horses, 3):
                horse1, odds1 = combo[0]
                horse2, odds2 = combo[1]
                horse3, odds3 = combo[2]
                total_odds = odds1 * odds2 * odds3
                self.add_bet_row("3連複", horse1, horse2, horse3, "", "", total_odds)

            if len(selected_horses) >= 2:
                for combo in combinations(selected_horses, 2):
                    horse1, odds1 = combo[0]
                    horse2, odds2 = combo[1]
                    avg_odds = (odds1 + odds2) / 2
                    self.add_bet_row("ワイド", horse1, horse2, "", "", "", avg_odds)

    def add_bet_row(self, bet_type, horse1, horse2, horse3, horse4, horse5, odds):
        row = self.bet_table.rowCount()
        self.bet_table.setRowCount(row + 1)
        self.bet_table.setItem(row, 0, QTableWidgetItem(bet_type))
        self.bet_table.setItem(row, 1, QTableWidgetItem(horse1))
        self.bet_table.setItem(row, 2, QTableWidgetItem(horse2))
        self.bet_table.setItem(row, 3, QTableWidgetItem(horse3))
        self.bet_table.setItem(row, 4, QTableWidgetItem(horse4))
        self.bet_table.setItem(row, 5, QTableWidgetItem(horse5))
        self.bet_table.setItem(row, 6, QTableWidgetItem(str(odds)))

    def parse_horse_data(self, data):
        horses = []
        entries = data.split('--')
        for entry in entries:
            if entry.strip():
                lines = entry.strip().split('\n')
                if len(lines) > 1:
                    name = lines[0].strip()
                    details = re.split(r'\s+', lines[1].strip())
                    if len(details) >= 6:
                        age_sex = details[0]
                        match = re.match(r"([牡牝セ])(\d+)", age_sex)
                        if match:
                            sex = match.group(1)
                            age = int(match.group(2))
                            odds = 0.0
                            if details[4]:
                                odds = float(details[4])
                            horse = {
                                "name": name,
                                "sex": sex,
                                "age": str(age),
                                "weight": str(details[1]),
                                "jockey": details[2],
                                "trainer": details[3],
                                "odds": str(odds),
                                "selected": False
                            }
                            horses.append(horse)
        return horses

    def set_style(self):
        style_sheet = """
            QMainWindow {
                background-color: #FFFFFF;
            }
            QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox, QTableWidget {
                color: #333333;
                background-color: #F5F5F5;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #007BFF;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #0056B3;
            }
            QHeaderView::section {
                color: #333333;
                background-color: #E0E0E0;
                border: 1px solid #CCCCCC;
                padding: 5px;
            }
            QTableWidget {
                alternate-background-color: #F9F9F9;
            }
        """
        self.setStyleSheet(style_sheet)

        palette = QPalette()
        palette.setColor(QPalette.WindowText, QColor(51, 51, 51))
        self.setPalette(palette)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BettingApp()
    window.show()
    sys.exit(app.exec())