import sys
from PyQt5.QtWidgets import QApplication
from ui import GenealogyApp
from tree_logic import FamilyTree

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Инициализация модели данных
    tree = FamilyTree()

    # Инициализация UI с названием MatsDrevo
    window = GenealogyApp(tree)
    window.show()

    sys.exit(app.exec_())