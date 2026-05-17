import json
import urllib.request
import ssl
from datetime import datetime, timedelta
import re

def fetch_dollar_quote():
    for days_back in range(3):
        target_date = datetime.now() - timedelta(days=days_back)
        fetch_date = target_date.strftime("%m-%d-%Y")
        url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarDia(dataCotacao=@dataCotacao)?@dataCotacao='{fetch_date}'"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MARSELO"})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                if data.get("value") and len(data["value"]) > 0:
                    val = data["value"][0].get("cotacaoVenda")
                    if val:
                        return val, target_date.strftime("%d/%m/%Y")
        except Exception as e:
            print(f"Error fetching data for {fetch_date}: {e}")
            continue

    return None, None


def main():
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    new_usd_val, new_usd_date = fetch_dollar_quote()
    if new_usd_val is not None:
        data["usd_to_brl"] = f"{new_usd_val:.2f}".replace(".", ",")
        data["usd_to_brl_day"] = new_usd_date

        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    with open("README.template.md", "r", encoding="utf-8") as f:
        template = f.read()

    for key in ["prog_langs", "databases", "devops_tools"]:
        if key in data and isinstance(data[key], list):
            data[key] = "<br>\n        ".join(data[key])

    if "now_fav_music_link" in data:
        data["now_fav_music_url"] = data["now_fav_music_link"].split(" ")[0]

    if "now_fav_video_link" in data:
        video_url = data["now_fav_video_link"].split(" ")[0]
        data["now_fav_video_url"] = video_url

        match = re.search(r"v[=:]+([^&]+)", video_url)
        if match:
            data["now_fav_video_id"] = match.group(1)
        else:
            data["now_fav_video_id"] = video_url.split("/")[-1]

    readme_content = template
    for key, value in data.items():
        if isinstance(value, str):
            readme_content = readme_content.replace(f"{{{{{key}}}}}", value)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("README.md updated successfully.")


if __name__ == "__main__":
    main()
