import openai
import PySimpleGUI as sg
import json
import time
import keyboard
import tkinter.font as font
#import pyi_splash


#try:
#    pyi_splash.close()
#except:
#    pass

####
openai.api_key = ''
####


#           Open Config File - Has API key and Theme
config_file = "config.json"

try:
    with open(config_file, "r") as f:
        config = json.load(f)
except FileNotFoundError:
    config = {}



#           Variable Storage
theme_list = sg.theme_list()
default_theme = 'GrayGrayGray'
memlimit = 5
totaltokens = 0
messagestorage = [{"role":"system","content":"You are a helpful assistant."}]
selected_theme = config.get("theme", default_theme)
openai.api_key = config.get("api",'')

#this function will be used to call the api and return the response
def helper_api_call(messagestorage) :
    try:
        query = openai.ChatCompletion.create(model="gpt-4", messages=messagestorage)
        print(query)
    except Exception as e:
        window['output'].update('Error: ' + str(e) + 'Press F12 + Send if you need to reinsert api key',append=True,justification='l',text_color='red')
        query = None  
    return query

#Run a timer while the api is being called updating the timer textbox
def display_timer():
    timer = 0
    window['timer'].update(visible=True)


    while window['timer'].visible==True:
        window['timer'].update(str(timer))
        timer += 1
        time.sleep(1)
        window.refresh()

       

#this function will be used to convert the hex color code to rgb
def hex_to_rgb(hex):
    """Return (red, green, blue) for the color given as #rrggbb."""
    if(hex[0] == '#'):
        hex = hex[1:]
    else:
        #black
        return (255,255,255)
    result = []
    hlen = len(hex)
    #return a list
    #use regex to extract the hex values
    for i in range(0, hlen, 2):
        result.append(int(hex[i:i+2],16))

        
    return result
def rgb_to_hex(rgb):
    """Return color as #rrggbb for the given color values."""
    return '#%02x%02x%02x' % rgb

    

# Load the configuration file or create an empty dictionary if it does not exist

# Get the stored PySimpleGUI theme or use the default theme
selected_theme = config.get("theme", default_theme)
openai.api_key = config.get("api",'')
sg.theme(selected_theme)
bgcolorstart = sg.theme_button_color_background()
theme_background_color = sg.theme_input_background_color()

bgcolor = hex_to_rgb(bgcolorstart)
theme_background_color = hex_to_rgb(theme_background_color)
shader_int = -20
divider_background_color = rgb_to_hex((theme_background_color[0]+shader_int,theme_background_color[1]+shader_int,theme_background_color[2]+shader_int))
line_height = 2
if bgcolorstart == '1234567890':
    bgcolorstart = 'black'


#if bgcolor is dark set the text color to white and if it is light set the text color to black
if bgcolor[0] < 128 and bgcolor[1] < 128 and bgcolor[2] < 128:
    textcolor = '#FF4500'
else:
    textcolor = '#f35390'
    

# GUI for the Top Left column - Currrently has the token counter and the memory limit
tokens_column = [
    [sg.Text(text="Tokens:", key="Tokens", auto_size_text=True, tooltip='This is the total number of tokens the last query cost', justification='left')],
    [sg.Text(text="Total Tokens:", auto_size_text=True, key="Total", tooltip='This is the total number of tokens for the session, 1000 tokens = .0006¢', justification='left')]
]
#Column for labels of the boxes
labels_column = [
    [sg.Push(),
    sg.Text(text='Message\nMemory',pad=((40,15),(0,0))),
    sg.Text(text="Instructor", key="Model", auto_size_text=True, tooltip='Set the mode of the GPT instructor, normal is chat bot mode, Teacher will explain things in depth and business should be more concise',
     justification='left',pad=((15,15),(0,0))),
    sg.Text(text="Theme", key="Theme", auto_size_text=True, tooltip='Set the theme of the window-this wont take affect till the next restart', justification='right',
            pad=((40,20),(0,0))),
    sg.Text(text = 'Model',key='model',auto_size_text=True,tooltip='This is the model that the bot will use to generate the response(Dall-E For images,Different GPT models)',pad=((50,0),(0,0))),
    sg.Push(),
    sg.Button(image_source='settings.png',key='settings',button_color=sg.theme_background_color(),border_width=0,tooltip='Settings',pad=((125,0),(0,0)))]
    #sg.Text(text="Append to output", key="appendt", auto_size_text=True, tooltip='Whatever is typed in this box will be added to the end of your request',
    #    justification='center')]
]

#GUI for the 
boxes_column = [
    [sg.DropDown(values=[i for i in range(1,11)], readonly=True,enable_events=True ,size=(5, 1),tooltip='This is how many previous messages will be sent with the current one so the bot can better understand the topic - more messages = better performance but cost more tokens.',
         key='memlim',default_value=memlimit,pad=((0,15),(0,0))),
    sg.DropDown(['Normal','Business','Teacher'],default_value='Normal',key='Instructor',readonly=True,enable_events=True,tooltip='Set the mode of the GPT instructor, normal is chat bot mode, Teacher will explain things in depth and business should be more concise',
        pad=((15,15),(0,0))),
    sg.Combo(theme_list,default_value=sg.theme(),key ='Theme2',readonly=True,size=10,enable_events=True,pad=((15,0),(0,0))),
    sg.DropDown(['GPT3','GPT4','DALL-E','DAVINCI'],default_value='GPT3',readonly=True,enable_events=True,tooltip='This is the model that the bot will use to generate the response(Dall-E For images,Different GPT models)',pad=((15,0),(0,0)))]
  #sg.Input( font=('Helvetica', 10),justification='l', key="append",pad=5,size=(20,1),tooltip='Whatever is typed in this box will be added to the end of your request')]
]


# GUI for the bottom column - Currently has the output box and the input box
input_output_column = [
    [sg.Multiline( font=('Sans Serif', 12), justification='right', key="output", expand_x=True, expand_y=True)],
    [sg.Multiline(font="italics",key="Input1", expand_x=True,
       no_scrollbar=True,enter_submits=True,focus=True,size=(50,2),enable_events=True,pad=((3,0),(5,0)),tooltip='Type your message here and press enter to send it to the bot'),
     sg.Button(image_source='send.png',key='Send', bind_return_key=True,button_color=sg.theme_input_background_color(),border_width=0,pad=((0),(3,0)) ),sg.Text(text='',key='timer',visible=False)]
]


layout = [
    [sg.Column(tokens_column,justification="left", element_justification="left",vertical_alignment='top',),
    sg.Column(labels_column,justification="left", element_justification="center",vertical_alignment='top',expand_x=True)],
    [sg.Column(boxes_column, justification="left",element_justification='center',expand_x=True,vertical_alignment='top')],
    [sg.Column(input_output_column,justification="c", element_justification="right",expand_x=True,expand_y=True,)],
]


window = sg.Window('Chatbot', layout,finalize=True,resizable=True)

# set the minumum window size - things get weird if you make it too small
width,height = window.get_screen_dimensions()
window.set_min_size((int(width/3)+70,int(height/2)))
input_window_width = window['Input1'].Widget.winfo_width()

while True:
    event, values = window.read()
    
    #if the message storage is greater than the memory limit remove the oldest message
    if len(messagestorage) > memlimit:
        messagestorage.pop(0)
    
    #when the window is closed or the exit button is pressed
    elif event == sg.WIN_CLOSED or event == 'Exit':
        sg.WINDOW_CLOSED
        break
    #when the theme preview button is pressed call the built in theme previewer
    elif event == 'Theme Preview':
        sg.theme_previewer()

    #when the theme is changed in the drop down menu
    elif event == 'Theme2':
        config['theme'] = values['Theme2']
        with open(config_file, "w") as f:
            json.dump(config, f)

    #when the memory limit is changed
    elif event == 'memlim':
        memlimit = values['memlim']
        if len(messagestorage) > memlimit:
            messagestorage = messagestorage[-memlimit:]

    #When you select a Instructor setting
    elif event == 'Instructor':
        messagestorage.clear
        if values['Instructor']=='Teacher':
           messagestorage.append({"role": "system", "content": "You are a teacher, explain things thoroughly and in depth"})
        elif values['Instructor']=='Business':
          messagestorage.append({"role": "system", "content": "You are a business man, professional and concise"})
        elif values['Instructor']=='Normal':
            messagestorage.append({"role": "system", "content": "You are a helpful assistant."})

    #when the multiline is type in
    elif event == 'Input1':
        #access the multliline widget
        len_of_inputtext =font.Font(family='italics', size=12).measure(values['Input1'])

        if input_window_width != window['Input1'].Widget.winfo_width():
            input_window_width = window['Input1'].Widget.winfo_width()
        #print the width of the multiline widget
        print(window['Input1'].get_size())
        print(len_of_inputtext)
        #if the length of the text is greater than the width of the multiline add lines limit to 10 lines
        print(max(line_height//2,1))
        if len_of_inputtext > (input_window_width*line_height)-25*max(line_height//2,1) and line_height < 10:
            line_height += 1
            window['Input1'].Widget.config(height=line_height)
            print(window['Input1'].get_size())
            print(len_of_inputtext)
        #if the length of the text is less than the width of the multiline add lines limit of 2 lines
        elif len_of_inputtext < (input_window_width*(line_height-1)-25*max(line_height//2,1)) and line_height > 2:
            line_height -= 1
            window['Input1'].Widget.config(height=line_height)

    #When you press f12 and activate another event to toggle the debug window
    elif  keyboard.is_pressed('F12') or (openai.api_key == '') or openai.api_key == None:
        #pop up the debug window
        tempapi =sg.PopupGetText('Insert API key here')
        #store the api key in the config file
        config['api'] = tempapi
        with open(config_file, "w") as f:
            json.dump(config, f)
        openai.api_key = tempapi
       
    ### Where the actual chatbot stuff happens ###

    #when the send button is pressed or enter is pressed
    elif (event == 'Send' or event == '_Enter') and values['Input1'] != '':
        #take the value of the input box and print it to the output box
        window['output'].update('User: '+values['Input1']+' '+'\n\n',append=True)  
        #clear the input box
        window['Input1'].update('')
        window['Input1'].Widget.config(height=2)
        line_height = 2                        
        messagestorage.append({"role": "user", "content": values["Input1"]})

        #pass the message to the helper function using the long operation function so the window doesnt freeze
        window.perform_long_operation(lambda :helper_api_call(messagestorage),'-END KEY-')
        window.perform_long_operation(display_timer,'endtimer')
        

    #when the helper function is done running
    if (event == '-END KEY-'):
        query = values['-END KEY-']
        window['timer'].update('',visible=False)
        
        if query is not None:
            messagestorage.append(query['choices'][0]['message'])
            output = str(query['choices'][0]['message']['content'])

            #replace the newlines
            
             #write to the multiline box
            window['output'].update('Bot: ',append=True,justification='l',text_color_for_value=textcolor)
            window['output'].update(str(output)+'\n',append=True,justification='l')
            window['output'].update('_'*50+'\n\n',justification='c',append=True,text_color_for_value=bgcolorstart,background_color_for_value=divider_background_color)
            print(bgcolorstart)
            #set thet okens for last query and total query
            
            #hex code for very light gray
            
            window['Tokens'].update('Tokens: '+ str(query['usage']['total_tokens']))
            totaltokens += query['usage']['total_tokens']
            window['Total'].update('Total Tokens: '+ str(totaltokens))
            #clear the input box
            
