
import os
os.sys.path.insert(0, os.getcwd())

import threading
from tkinter import *

from rede.rede_simu import Network


def str2int(string):
    return int(''.join(c for c in string if c.isdigit()))

def change_state(network, switch_name):
    print('Change state of', switch_name)
    current_state = network.read(switch_name)

    if current_state == 'open':
        desired_state = 'close'
    elif current_state == 'close':
        desired_state = 'open'
    
    network.operate(switch_name, desired_state)
    
def update_fields(window, network, fields):
    switch_buttons, segment_texts, consumers_texts = fields
    
    # Switches
    switch_button_colors = {
        'open': 'grey',
        'close': 'lime'
    }
    for switch_name, button in switch_buttons.items():
        switch_state = network.read(switch_name)
        button.configure(bg = switch_button_colors[switch_state])

    # # Trechos
    # for segment_name, text_area in segment_texts.items():
    #     segment_current = network.read_segments_load(segment_name)
    #     value = round(segment_current.mod, 2)
    #     text_area.config(text=f'{segment_name}: {value} A')
    
    # # Nos
    # for consumer_name, text_area in consumers_texts.items():
    #     consumer_voltage = network.read_energy_consumers_voltage(consumer_name)
    #     value = round(consumer_voltage.mod, 2)
    #     text_area.config(text=f'{consumer_name}: {value} V')

    # Keep updating
    window.after(100, lambda: update_fields(window, network, fields))

if __name__ == "__main__":

    # Instancia rede
    network_filename = os.sys.argv[1]
    ip_ied_filename = os.sys.argv[2]
    network = Network(network_filename, ip_ied_filename)
 
    # Configura GUI
    window = Tk()
    window.title("Simulação de Rede")
    # window.geometry('350x200')

    # Chaves
    switch_buttons = {}
    for index, chave in enumerate(sorted(network.chaves.values(), key=lambda chave: chave.nome)):
        button_name = chave.nome
        button = Button(window, text=button_name, command=(lambda name=button_name: change_state(network, name)))
        button.grid(column=0, row=index)
        switch_buttons[button_name] = button

    # Trechos
    segment_texts = {}
    # for index, trecho in enumerate(network.trechos.values()):
    #     nome_trecho = trecho.nome
    #     text = Label(window)
    #     text.grid(column=1+index//len(switch_buttons), row=index%len(switch_buttons))
    #     segment_texts[nome_trecho] = text

    # Nos
    # last_column = 2+index//len(switch_buttons)
    consumers_texts = {}
    # for index, no in enumerate(network.nos.values()):
    #     nome_no = no.nome
    #     text = Label(window)
    #     text.grid(column=last_column+index//len(switch_buttons), row=index%len(switch_buttons))
    #     consumers_texts[nome_no] = text
    
    # Executa rede em novo processo
    p = threading.Thread(target=network.run)
    p.start()

    # Programa atualização
    fields = (switch_buttons, segment_texts, consumers_texts)
    window.after(100, lambda: update_fields(window, network, fields))
    
    # Executa loop da GUI
    window.mainloop()
