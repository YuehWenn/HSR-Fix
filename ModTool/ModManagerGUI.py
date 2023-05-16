import PySimpleGUI as sg
import os
import configparser

if __name__ == "__main__":
    """
    A neat and simple GUI for Shader Hacker.
    
    Files->Open:    Choose a Mods folder.
    Help->About:    Show author info.
    
    """

    # Define a menu

    menu_def = [
        ['Files', ['Open']],
        ['Help', ['About']]
    ]

    # Define the main layout of program
    layout = [
        [sg.Menu(menu_def)]
    ]

    # Create the Window
    window = sg.Window('Shader Freedom Mod Manager V0.1', layout, size=(1000, 671),resizable=True)

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
            break

        if event == "About":
            print("Author :NicoMico")
            pass

        if event == "Open":
            # choose a Mods folder to read mods
            ModsFolder = sg.popup_get_folder('Choose your 3Dmigoto Mods folder', keep_on_top=True)
            # os.listdir to get all mod folders

            print(ModsFolder)
            pass

        print('You entered ', values[0])

    window.close()
