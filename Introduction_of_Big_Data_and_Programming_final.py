import requests
from bs4 import BeautifulSoup as bs
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from tkinter import*
import tkinter as tk
from tkinter import ttk

import json
import os
import sys
# -- coding: utf-8 --**

config = {
    'data_file_name': 'data.txt',
    'temp_file_name': 'temp.json'
}


class Fetcher:
    @staticmethod
    def findNumberInString(s: str) -> tuple:
        size = len(s)
        l = 0
        while l < size and (s[l] > '9' or s[l] < '0'):
            l = l + 1

        r = l + 1
        while r < size and (s[r] == "," or s[r] == "." or (s[r] <= '9' and s[r] >= '0')):
            r = r + 1

        result = str()
        while l < r:
            if s[l] != ',':
                result = result + s[l]
            l = l + 1
        if r < size:
            if s[r] == '萬':
                return (result, 1)
            elif s[r] == '億':
                return (result, 2)
        return (result, 0)

    @staticmethod
    def findValidIndexInScript(all_script: list) -> int:
        if len(all_script[34].get_text()) > 17 and all_script[34].get_text()[4:17] == "ytInitialData":
            return 34
        else:
            size = len(all_script)
            for i in range(0, size):
                text = all_script[i].get_text()
                if len(text) > 100 and text[4:17] == "ytInitialData":
                    return i
        return -1

    @staticmethod
    def DecimalPointPos(s: str) -> int:
        for i in range(len(s)):
            if s[i] == '.':
                return i
        return -1

    def __init__(self):
        self.dir_path = str()
        if getattr(sys, 'frozen', False):
            self.dir_path = os.path.dirname(sys.executable)
        elif __file__:
            self.dir_path = os.path.dirname(__file__)

    def setDataPath(self, path: str) -> None:
        self.search_data_path = self.dir_path
        self.search_data_path += "/"
        self.search_data_path += path

        # Check if the data file exists
        if not os.path.exists(self.search_data_path):
            print("The data file does not exist!")
            exit(0)

    def setUpClass(self):
        self.search_url = []
        self.search_name = []
        self.subscriber_count_result = []
        self.viewing_count_result = []
        self.results = []

        # Set the window
        self.root = tk.Tk()
        self.root.state("zoomed")  # full screen
        tk.Label(self.root, text='Youtuber Imformation').pack()
        self.root.title("Youtuber Imformation")

        # Open the file containg the searching data and store the data in tuple formation
        with open(self.search_data_path, encoding='utf-8') as data_file:
            for line in data_file:
                sep = line.split(',')
                self.search_url.append(sep[0].strip())
                self.search_name.append(sep[1].strip())

    def search(self):
        size = len(self.search_name)
        for i in range(0, size):
            url = "https://www.youtube.com/" + self.search_url[i] + "/about"
            html = requests.get(url)

            soup = bs(html.content.decode("utf-8"), 'html.parser')
            all_scripts = soup.find_all('script')
            index = self.findValidIndexInScript(all_scripts)
            script = all_scripts[index].get_text()[20:-1]

            temp_file_path = self.dir_path + \
                '/' + config['temp_file_name']

            json_file = open(temp_file_path, "w", encoding='utf-8')
            json_file.write(script)
            json_file.close()

            with open(temp_file_path, encoding='utf-8') as json_file:
                json_data = json.load(json_file)

            subscriber_count = str(json_data['header']['c4TabbedHeaderRenderer']
                                   ['subscriberCountText']['simpleText'])

            temp = json_data['contents']['twoColumnBrowseResultsRenderer']['tabs']
            index = len(temp) - 2
            viewing_count = (temp[index]['tabRenderer']['content']['sectionListRenderer']['contents'][0][
                'itemSectionRenderer']['contents'][0]['channelAboutFullMetadataRenderer']['viewCountText']['simpleText'])

            self.subscriber_count_result.append(
                self.findNumberInString(subscriber_count))
            self.viewing_count_result.append(
                int(self.findNumberInString(viewing_count)[0]))
        os.remove(temp_file_path)

    def showChart(self):
        size = len(self.search_name)
        x = np.arange(size)

        # Determine the real number of subscriber
        subscriber_result = []
        for data in self.subscriber_count_result:
            match (data[1]):
                case 0:
                    subscriber_result.append(int(data[0]))

                case 1:
                    pos = self.DecimalPointPos(data[0])
                    if pos != -1:
                        result = data[0][0: pos]
                        decimal = data[0][pos + 1:]
                        result += decimal
                        for i in range(4 - len(decimal)):
                            result += "0"
                    else:
                        result = data[0] + "0000"
                    subscriber_result.append(int(result))

                case 2:
                    pos = self.DecimalPointPos(data[0])
                    if pos != -1:
                        result = data[0][0: pos]
                        decimal = data[0][pos + 1:]
                        result += decimal
                        for i in range(8 - len(decimal)):
                            result += "0"
                    else:
                        result = data[0] + "00000000"

                    subscriber_result.append(int(result))

        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']

        f = Figure(figsize=(5, 4), dpi=100)
        a = f.add_subplot(1, 2, 1)
        a.bar(x, subscriber_result, color='#ba9c65')
        a.set_xticks(x)
        a.set_xlabel('Youtuber')
        a.set_ylabel('Subscriber Count')

        b = f.add_subplot(1, 2, 2)
        b.bar(x, self.viewing_count_result, color='#ba9c65')
        b.set_xticks(x)
        b.set_xlabel('Youtuber')
        b.set_ylabel('Viewer Count')

        canvas = FigureCanvasTkAgg(f, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

        toolbar = NavigationToolbar2Tk(canvas, self.root)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

    def showSheet(self):
        size = len(self.viewing_count_result)
        label = ('Index', 'Youtuber', '訂閱數', '觀看數')
        id = ('a0', 'a1', 'a2', 'a3')
        label_width = [10, 200, 200, 200]
        data = []

        # Determine the real number of subscriber
        for i in range(0, size):
            subscriber_result = str(self.subscriber_count_result[i][0])
            match (self.subscriber_count_result[i][1]):
                case 0:
                    pass
                case 1:
                    subscriber_result = subscriber_result + "萬"
                case 2:
                    subscriber_result = subscriber_result + "億"

            data.append(
                (i, self.search_name[i], subscriber_result, self.viewing_count_result[i]))

        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Microsoft JhengHei', 13))
        style.configure("Treeview", rowheight=30,
                        font=('Microsoft JhengHei', 13))

        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill='x')

        tv = ttk.Treeview(table_frame,
                          columns=id,
                          show='headings',
                          height=10)

        for i in range(0, 4):
            tv.column(id[i], width=label_width[i], anchor='w')
            tv.heading(id[i], text=label[i], anchor='w')
        tv.pack(fill='x')
        for i in range(0, size):
            tv.insert('', 'end', values=data[i])

    def showResult(self):
        self.showChart()
        self.showSheet()
        self.root.mainloop()

    def Run(self):
        print("Processing...")
        self.setDataPath(config['data_file_name'])
        self.setUpClass()
        self.search()
        print("Done!")
        self.showResult()


if __name__ == '__main__':
    fetcher = Fetcher()
    fetcher.Run()
