import subprocess

sets = [
    ("utils", "ec2-user@3.71.28.242:/home/ec2-user/python/discordSpaceTradeBot/"),
    ("game_logic", "ec2-user@3.71.28.242:/home/ec2-user/python/discordSpaceTradeBot/"),
]
files = [
    (".env", "ec2-user@3.71.28.242:/home/ec2-user/python/discordSpaceTradeBot/"),
    (
        "requirements.txt",
        "ec2-user@3.71.28.242:/home/ec2-user/python/discordSpaceTradeBot/",
    ),
    ("main.py", "ec2-user@3.71.28.242:/home/ec2-user/python/discordSpaceTradeBot/"),
]

if __name__ == "__main__":
    for local, cloud in sets:
        p = subprocess.Popen(f"scp -r -i discord_bot_aws_key_rsa.pem {local} {cloud}")
        sts = p.wait()
    for local, cloud in files:
        p = subprocess.Popen(f"scp -i discord_bot_aws_key_rsa.pem {local} {cloud}")
        sts = p.wait()
