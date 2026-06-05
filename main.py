import os

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def show_menu():
    print("***************************")
    print("*** M165: MEILENSTEIN 2 ***")
    print("***************************\n")
    print("1: Kurs suchen")
    print("2: Teilnehmer/in erfassen")
    print("3: Teilnehmerstatus aktualisieren")
    print("4: Teilnehmer/in löschen (Bonus)")
    print("5: Kursdauer ändern (Bonus)")
    print()
    print("Deine Auswahl: ", end="")


def return_to_menu():
    input("\nEine Taste drücken, um zum Menü zurückzukehren...")
    clear_console()


def main():
    while True:
        show_menu()

        user_choice = input()

        clear_console()

        if user_choice == "1":

            pass

        elif user_choice == "2":

            pass

        elif user_choice == "3":

            pass

        elif user_choice == "4":

            pass

        elif user_choice == "5":

            pass

        else:
            print("Ungültige Eingabe.")

        return_to_menu()


if __name__ == "__main__":
    main()