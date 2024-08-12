import time
import chromedriver_autoinstaller
import os
import sys
import re
import shutil
import numpy as np
from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.progress import track
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from tkinter import Tk
from tkinter.filedialog import askopenfilename


chromedriver_autoinstaller.install()


def setup_drivers():
    data_path = os.getcwd() + "/data"
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(rf"--user-data-dir={data_path}")
    options.add_argument("--no-sandbox")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")

    chromedriver = webdriver.Chrome(options=options)
    wait = WebDriverWait(chromedriver, 30)
    return chromedriver, wait


def getProfileNames(chromedriver, wait):
    chromedriver.get("https://www.youtube.com")
    top_btn_xPath = """//*[@id="img"]"""
    wait.until(EC.element_to_be_clickable((By.XPATH, top_btn_xPath))).click()
    switch_acc_btn_xPath = """/html/body/ytd-app/ytd-popup-container/tp-yt-iron-dropdown/div/ytd-multi-page-menu-renderer/div[3]/div[1]/yt-multi-page-menu-section-renderer[1]/div[2]/ytd-compact-link-renderer[2]/a"""
    wait.until(EC.element_to_be_clickable((By.XPATH, switch_acc_btn_xPath))).click()
    time.sleep(2)
    email_elements = chromedriver.find_elements(by="xpath",value="""//*[@id="contents"]/ytd-account-item-renderer""")
    profileNames = [elem.text.split("\n")[0] for elem in email_elements]
    return profileNames

def switchProfile(chromedriver, wait, profileName):
    chromedriver.get("https://www.youtube.com")
    top_btn_xPath = """//*[@id="img"]"""
    wait.until(EC.element_to_be_clickable((By.XPATH, top_btn_xPath))).click()
    switch_acc_btn_xPath = """/html/body/ytd-app/ytd-popup-container/tp-yt-iron-dropdown/div/ytd-multi-page-menu-renderer/div[3]/div[1]/yt-multi-page-menu-section-renderer[1]/div[2]/ytd-compact-link-renderer[2]/a"""
    wait.until(EC.element_to_be_clickable((By.XPATH, switch_acc_btn_xPath))).click()
    time.sleep(2)
    email_elements = chromedriver.find_elements(by="xpath",value="""//*[@id="contents"]/ytd-account-item-renderer""")
    for elem in email_elements:
        if elem.text.split("\n")[0] == profileName:
            wait.until(EC.element_to_be_clickable(elem)).click()
            return True
    return False

def get_subscriptions(chromedriver, save_to_file=False):
    chromedriver.get("https://www.youtube.com/feed/channels")
    script = """
    var pageHeight = 0;
    function findHighestNode(nodesList) {
        for (var i = nodesList.length - 1; i >= 0; i--) {
            if (nodesList[i].scrollHeight && nodesList[i].clientHeight) {
                var elHeight = Math.max(nodesList[i].scrollHeight, nodesList[i].clientHeight);
                pageHeight = Math.max(elHeight, pageHeight);
            }
            if (nodesList[i].childNodes.length) findHighestNode(nodesList[i].childNodes);
        }
    }
    
    findHighestNode(document.documentElement.childNodes);
    window.scrollTo(0, pageHeight);
    pageHeight = 0;
    findHighestNode(document.documentElement.childNodes);
    return pageHeight
    """
    lenOfPage = chromedriver.execute_script(script)
    match = False
    while match == False:
        lastCount = lenOfPage
        time.sleep(3)
        lenOfPage = chromedriver.execute_script(script)
        if lastCount == lenOfPage:
            match = True
    html = chromedriver.page_source
    finder = re.compile(
        r"""<a class="channel-link yt-simple-endpoint style-scope ytd-channel-renderer(.+?)>"""
    )
    subHrefs = finder.findall(html)
    subList = []
    for sub in subHrefs:
        subList.append(sub.split("href=")[1].split("/")[1][:-1])
    if save_to_file:
        subs_array = np.array(subList)
        np.savetxt("subs.csv", subs_array, delimiter=",", fmt="%s", encoding="utf-8")
    return subList

def subscriber(chromedriver, wait, subs_list):
    for sub in subs_list:
        chromedriver.get(f"https://www.youtube.com/{sub}")
        subscribe_xpath = """//*[@id="page-header"]/yt-page-header-renderer/yt-page-header-view-model/div/div[1]/div/yt-flexible-actions-view-model/div/yt-subscribe-button-view-model/yt-animated-action/div[1]/div[2]/button"""
        wait.until(EC.element_to_be_clickable((By.XPATH, subscribe_xpath))).click()

def exit_program(chromedriver=None):
    if(chromedriver != None):
        chromedriver.close()
        data_path = os.getcwd() + "\\data"
        os.system("clear")
        print("Deleting temp files....")
        try:
            shutil.rmtree(data_path)
            print("Deleted temp files. Exiting...")
        except:
            print("Error deleting temp files. Manually delete data folder.\nExiting...")
    time.sleep(2)
    os.system("clear")
    sys.exit()

def main_menu():
    os.system("clear")
    menu = """
    1. Save subs list to csv.\n
    2. Copy subs from csv.\n
    3. Copy subs from one profile to another.\n
    4. Initial Setup.\n
    5. Exit.\n"""
    print(Panel(menu, title="Youtube Subscriptions Copy"))
def choose_profile(profileNames):
    os.system("clear")
    menu = ""
    for index in range(len(profileNames)):
        menu += f"{index+1}. {profileNames[index]}\n"
    print(Panel(menu, title="Profile List"))
    

while True:
    main_menu()
    console = Console()
    option = console.input("Choose an option : ")
    os.system("clear")
    if option == "1":
        chromedriver, wait = setup_drivers()
        profileNames = getProfileNames(chromedriver, wait)
        choose_profile(profileNames)
        profileIndex = console.input("Choose profile to which subs are to be copied : ")
        switchProfile(chromedriver, wait, profileNames[int(profileIndex)-1])
        get_subscriptions(chromedriver, save_to_file=True)
        chromedriver.close()
    elif option == "2":
        Tk().withdraw()
        filename = askopenfilename(filetypes=[("CSV Files", "*.csv")])
        subs_list = list(
            np.genfromtxt(filename, delimiter=",", dtype=str, encoding="utf-8")
        )
        chromedriver, wait = setup_drivers()
        profileNames = getProfileNames(chromedriver, wait)
        choose_profile(profileNames)
        profileIndex = console.input("Choose profile to which subs are to be copied : ")
        switchProfile(chromedriver, wait, profileNames[int(profileIndex)-1])
        subscriber(chromedriver, wait, subs_list)
        chromedriver.close()
    elif option == "3":
        chromedriver, wait = setup_drivers()
        profileNames = getProfileNames(chromedriver, wait)
        choose_profile(profileNames)
        profileIndex = console.input("Choose profile to which subs are to be copied from : ")
        switchProfile(chromedriver, wait, profileNames[int(profileIndex)-1])
        subs_list = get_subscriptions(chromedriver)
        choose_profile(profileNames)
        profileIndex = console.input("Choose profile to which subs are to be copied to : ")
        switchProfile(chromedriver, wait, profileNames[int(profileIndex)-1])
        subscriber(chromedriver, wait, subs_list)
        chromedriver.close()
    elif option == "4":
        os.system("clear")
        chromedriver, wait = setup_drivers()
        chromedriver.get("https://www.youtube.com")
        console.input("Login to both accounts and press ENTER")
        print("Initial Setup Done")
        time.sleep(3)
    elif option == "5":
        exit_program()
