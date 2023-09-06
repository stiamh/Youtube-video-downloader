from tkinter import *
from tkinter import font
from tkinter.messagebox import showinfo, showerror
from tkinter import ttk
from pytube import YouTube
import os
from lists import titles, links
import random
import configparser
import threading
import webbrowser

# Create the config parser for the users settings. 
config = configparser.ConfigParser() 
config.read("settings.ini")

#Create the window.
root = Tk()
root.resizable(width = False, height = False)
root.title(random.choice(titles))
root.geometry("500x250")
root.iconbitmap("images/icon.ico")
background_colour = config["SETTINGS"]["background_colour"]
root.config(bg = background_colour)

#Creates the menu bar + adds items and cascades.
menubar = Menu(root)
root.config(menu=menubar)

# Image, Welcome Label, and Background section
icon_help = os.getcwd() # Just here so the icon bitmap doesn't throw an error when accessing settings after changing the directory

logo = PhotoImage(file = f"{icon_help}\images\psyduck.jpg")
logo = logo.subsample(4, 4)

# Settings window section
def settings():
    settings_root = Tk()
    settings_root.resizable(width = False, height = False)
    settings_root.config(bg = background_colour)
    settings_root.title("Settings")
    settings_root.geometry("475x175")
    settings_root.iconbitmap(f"{icon_help}\images\icon.ico")

    save_location_label = Label(settings_root, text = "Save Location Path:", padx= 20, pady= 20, bg = background_colour)
    save_location_label.grid(column = 0, row = 0)
    save_location_txt = Entry(settings_root, width = 50)
    save_location_txt.insert(0, config["SETTINGS"]["save_location"])
    save_location_txt.grid(column = 1, row = 0, columnspan = 3)

    colour_options_label = Label(settings_root, text = "Enter a colour code:", padx = 20, pady = 20, background = background_colour)
    colour_options_label.grid(column = 0, row = 1)
    colour_options_txt = Entry(settings_root, width = 50)
    colour_options_txt.insert(0, config["SETTINGS"]["background_colour"])
    colour_options_txt.grid(column = 1, row = 1, columnspan = 3)

    def save():
        with open("settings.ini", "w") as configfile:
            saved_location = save_location_txt.get()
            new_colour = colour_options_txt.get()
            config.set("SETTINGS", "save_location", f"{saved_location}")
            config.set("SETTINGS", "background_colour", f"{new_colour}")
            config.write(configfile)
            configfile.close()

            save_label = Label(settings_root, text = "Saved! :)", padx = 10, pady = 10, bg = background_colour, font = Custom_font)
            save_label.grid(column = 0, row = 2)

    update_btn = Button(settings_root, text = "Save", fg = "black", command = save)
    update_btn.grid(column = 2, row = 2)

def RainbowLabel():
    rainbow_colors = ['red','orange','yellow','green','blue', 'indigo','violet']
    colour = random.choice(rainbow_colors)
    welcome.config(bg = colour)
    welcome.after("100", RainbowLabel)

       
Button(root, image = logo, command = lambda: webbrowser.open(random.choice(links))).grid(column = 0, row = 0, padx = 10, pady = 10, columnspan = 2, rowspan = 2)
Custom_font = font.Font( family = "Comic Sans MS", size = 15, weight = "bold")
welcome = Label(root, text = "Youtube to MP3/MP4 Converter", font = Custom_font)
welcome.grid(column = 2, row = 0, columnspan = 6, padx = 10, pady = 10)
RainbowLabel()

#Creates a settings tab and exit tab within the menu
settings_menu = Menu(menubar, tearoff = False)
settings_menu.add_command(label = "Settings", command = settings)
menubar.add_cascade(label = "Settings", menu = settings_menu)

exit_menu = Menu(menubar, tearoff = False)
exit_menu.add_command(label = "Exit", command = root.destroy)
menubar.add_cascade(label = "Exit", menu = exit_menu, command = root.destroy)

# Creates Radio Buttons for mp3 or mp4
bool_var = BooleanVar()
    
mp3 = Radiobutton(root, text = "MP3", variable = bool_var, value = False, bg = background_colour)
mp3.select()
mp3.grid(column = 3, row = 1)
mp4 = Radiobutton(root, text = "MP4", variable = bool_var, value = True, bg = background_colour)
mp4.grid(column = 4, row = 1)

url_label = Label(root, text = "Enter Youtube URL:", padx = 10, pady = 10, bg = background_colour)
url_label.grid(column = 0, row = 3)

url_txt = Entry(root, width = 50)
url_txt.grid(column = 2, row = 3, columnspan = 5)

def submit(): 
    os.chdir(f"{config['SETTINGS']['save_location']}")
    url_link = url_txt.get()
    if url_link == "":
        showerror(title = "Error", message = "Please enter a Youtube URL :)")
    else:
        try:
            # function for tracking the progress bar.
            def progress(stream, chunk, bytes_remaining):
                total_size = stream.filesize

                # Gets the total size of the Youtube download. units are for btye sizes.
                def get_formatted_size(total_size, factor = 1024, suffix = "B"):
                    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
                        if total_size < factor:
                            return f"{total_size:.2f}{unit}{suffix}"
                        total_size /= factor
                    return f"{total_size:.2f}Y{suffix}"
                
                formatted_size = get_formatted_size(total_size)
                bytes_downloaded = total_size - bytes_remaining
                percentage_completed = round(bytes_downloaded / total_size * 100)
                progress_bar["value"] = percentage_completed
                progress_bar_label.config(text=str(percentage_completed) + "%, File size:" + formatted_size)
                root.update()
            
            # download mp3 / mp4
            format = bool_var.get()
            if format == False:
                audio = YouTube(url_link, on_progress_callback = progress)
                audio_output = audio.streams.get_audio_only().download()
                base, ext = os.path.splitext(audio_output)
                file = base + ".mp3"
                os.rename(audio_output, file)
                showinfo(title = "Download Complete", message = "MP3 has been downloaded successfully.") 
            elif format == True:
                video = YouTube(url_link, on_progress_callback = progress)
                video_output = video.streams.filter(progressive = True, file_extension='mp4').order_by('resolution').desc().first() # This just sorts the streams fom highest to lowest and picks the first one. The progressive means its a stream not using "DASH", so it has both audio + video.
                video_output.download()
                showinfo(title = "Download Complete", message = "MP4 has been downloaded successfully.")
        except:
            showerror(title = "Download Error", message = "An error occurred while trying to " \
                    "download the MP3/MP4\nThe following could " \
                    "be the causes:\n->Invalid link\n->No internet connection\n->File exists with the same name\n"\
                     "Make sure you have stable internet connection and the Youtube link is valid")
        progress_bar_label.config(text = "")
        progress_bar["value"] = 0

# Thread for download so it runs smoother.
def downloadThread():
    t1 = threading.Thread(target = submit)
    t1.start()

submit_btn = Button(root, text = "Submit", fg = "black", command = submit)
submit_btn.grid(column = 3, row = 4, columnspan = 2)

progress_bar_label = Label(root, text='')
progress_bar = ttk.Progressbar(root, orient = HORIZONTAL, length = 480, mode = "determinate")
progress_bar.grid(column = 0, row = 5, columnspan = 8, padx = 10, pady = 10)

if config["SETTINGS"]["save_location"] == "":
    settings()

root.mainloop()