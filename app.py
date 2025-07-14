# APP DESIGN

from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QComboBox, QDateEdit, QTableWidget,
    QVBoxLayout, QHBoxLayout, QMessageBox, QTableWidgetItem, QHeaderView, QSpinBox, QToolTip
    )

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QCursor

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from database import fetch_expenses, add_expenses, delete_expenses

class ExpenseApp(QWidget) :

    def __init__(self):
        super().__init__()
        self.settings()
        self.initUI()
        self.load_table_data()

    def settings(self):
        self.resize(700, 600)
        self.setWindowTitle("Finance Manager")
        screen = self.screen().availableGeometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

    def initUI(self):
        # Input widgets
        self.date_box = QDateEdit()
        self.date_box.setDate(QDate.currentDate())
        self.date_box.setCalendarPopup(True)

        self.dropdown = QComboBox()
        self.populate_dropdown()

        self.amount = QLineEdit()
        self.amount.setPlaceholderText("Enter amount")

        self.description = QLineEdit()
        self.description.setPlaceholderText("Enter description")

        self.split_spin = QSpinBox()
        self.split_spin.setMinimum(1)
        self.split_spin.setValue(1)

        # Buttons
        self.btn_add = QPushButton("Add Expense")
        self.btn_delete = QPushButton("Delete Expense")

        # Table setup
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Category", "Amount", "Description", "Split Count"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setColumnHidden(5, True)
        self.table.setAlternatingRowColors(True)
        self.table.cellEntered.connect(self.show_tooltip)

        # Total spent label and pie chart canvas
        self.total_label = QLabel("Total Spent: ₹0.00")
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        # Layouts
        layout = QVBoxLayout()
        top = QHBoxLayout()
        form = QVBoxLayout()

        form.addWidget(QLabel("Date"))
        form.addWidget(self.date_box)
        form.addWidget(QLabel("Category"))
        form.addWidget(self.dropdown)
        form.addWidget(QLabel("Amount"))
        form.addWidget(self.amount)
        form.addWidget(QLabel("Description"))
        form.addWidget(self.description)
        form.addWidget(QLabel("Split Count"))
        form.addWidget(self.split_spin)

        top.addLayout(form)

        right = QVBoxLayout()
        right.addWidget(self.btn_add)
        right.addWidget(self.btn_delete)
        right.addSpacing(20)
        right.addWidget(self.total_label)
        right.addWidget(self.canvas)
        top.addLayout(right)

        layout.addLayout(top)
        layout.addWidget(self.table)
        self.setLayout(layout)

        # Connect buttons
        self.btn_add.clicked.connect(self.add_expense)
        self.btn_delete.clicked.connect(self.delete_expense)

        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f8f6;
                font-family: 'Segoe UI', 'Arial', 'Sans-Serif';
                font-size: 14px;
            }

            QLabel {
                font-weight: bold;
                font-size: 13px;
                color: #3c3c3c;
            }
            QLineEdit, QComboBox, QDateEdit, QSpinBox {
                background-color: #ffffff;
                border: 1.5px solid #dcdcdc;
                border-radius: 10px;
                padding: 6px 10px;
                color: black;  /* Add this */
            }
            QPushButton {
                background-color: #33415c;
                color: white;
                border-radius: 10px;
                padding: 10px 18px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #3c4f65;
            }
            QTableWidget {
                background-color: #ffffff;
                border-radius: 12px;
                alternate-background-color: #f2f2f2;
                color: #333333;  /* Dark text for table items */
            }

            QTableWidget::item {
                color: #333333;  /* Ensures table cell text is dark */
            }

            QHeaderView::section {
                background-color: #33415c;
                color: white;
                font-weight: bold;
                padding: 6px;
            }
                           
            QComboBox QAbstractItemView {
                background-color: #ffffff;       /* Dropdown list background */
                color: #333333;                  /* Dropdown list text */
                selection-background-color: #33415c;  /* Highlight background */
                selection-color: white;         /* Highlighted text */
            }

        """)

    def populate_dropdown(self):
        self.dropdown.addItems(["Food", "Rent", "Bills", "Entertainment", "Shopping", "Others"])

    def load_table_data(self):
        expenses = fetch_expenses()
        self.table.setRowCount(0)
        self.expenses_data = []

        for row_idx, (eid, date, category, amount, description, split_count) in enumerate(expenses):
            share = amount / split_count if split_count > 0 else amount

            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(eid)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(date))
            self.table.setItem(row_idx, 2, QTableWidgetItem(category))

            amt_item = QTableWidgetItem(f"₹{share:.2f}")
            amt_item.setData(Qt.ItemDataRole.UserRole, (amount, split_count))
            self.table.setItem(row_idx, 3, amt_item)

            self.table.setItem(row_idx, 4, QTableWidgetItem(description))
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(split_count)))
            self.expenses_data.append((category, share))

        self.update_pie_chart()

    def update_pie_chart(self):
        self.ax.clear()
        totals = {}
        for cat, amt in self.expenses_data:
            totals[cat] = totals.get(cat, 0) + amt

        if not totals:
            self.total_label.setText("Total Spent: ₹0.00")
            self.canvas.draw()
            return

        categories, amounts = list(totals.keys()), list(totals.values())
        pastel = ["#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF", "#D7BAFF"]
        self.ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90, colors=pastel)
        self.ax.axis("equal")
        self.total_label.setText(f"Total Spent: ₹{sum(amounts):.2f}")
        self.canvas.draw()

    def add_expense(self):
        date = self.date_box.date().toString("yyyy-MM-dd")
        category = self.dropdown.currentText()
        amount = self.amount.text().strip()
        description = self.description.text().strip()
        split_count = self.split_spin.value()

        # Validation
        if not (date and category and amount and split_count):
            QMessageBox.warning(self, "Missing Fields", "Please fill in all required fields.")
            return

        try:
            amount = float(amount)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Amount must be a number.")
            return

        # Add to DB
        add_expenses(date, category, amount, description, split_count)
        self.load_table_data()
        self.update_pie_chart()

        # Clear inputs
        self.clear_inputs()

    def delete_expense(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Error", "Select a row to delete")
            return
        eid = int(self.table.item(row, 0).text())
        confirm = QMessageBox.question(self, "Confirm", "Are you sure?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            if delete_expenses(eid):
                self.load_table_data()
                self.update_pie_chart()

    def clear_inputs(self):
        self.date_box.setDate(QDate.currentDate())
        self.dropdown.setCurrentIndex(0)
        self.amount.clear()
        self.description.clear()
        self.split_spin.setValue(1)

    def show_tooltip(self, row, column):
        if column == 3:
            item = self.table.item(row, column)
            if item:
                amount, split = item.data(Qt.ItemDataRole.UserRole)
                if split > 1:
                    tip = f"Original: ₹{amount:.2f}\nSplit: {split} people"
                    QToolTip.showText(QCursor.pos(), tip, self.table.viewport())

