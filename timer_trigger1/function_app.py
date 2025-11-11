
import datetime
import logging
import os
import requests
import azure.functions as func

# Explicitly configure logging to output to console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



def call_weather_api_and_get_data():
    api_url = os.getenv("PUBLIC_WEATHER_DATA_API_ENDPOINT")
    api_key = os.getenv("PUBLIC_WEATHER_DATA_API_KEY")

    try:
        if not api_url or not api_key:
            raise ValueError("환경변수 PUBLIC_WEATHER_DATA_API_ENDPOINT 또는 PUBLIC_WEATHER_DATA_API_KEY가 설정되지 않았습니다.")

        now_utc = datetime.datetime.utcnow()
        one_hour_ago_utc = now_utc - datetime.timedelta(hours=1)

        params = {
            "tm1": one_hour_ago_utc.strftime("201512110100"),
            "tm2": now_utc.strftime("201512140000"),
            "stn": "108",
            "help": "1",
            "authKey": api_key,
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(api_url, params=params, headers=headers)
        response.raise_for_status()
        logging.info("날씨 API 호출 성공")
        return response.text

    except Exception as e:
        logging.error("날씨 API 호출 실패: %s", e)
        return None

def main(timer_trigger1: func.TimerRequest, outputEventHub: func.Out[str]) -> None:
    utc_timestamp = datetime.datetime.utcnow().isoformat()
    logging.info('Timer trigger executed at %s', utc_timestamp)

    weather_data = call_weather_api_and_get_data()
    if weather_data:
        logging.info("날씨 데이터 Event Hub로 전송: %s", weather_data)
        outputEventHub.set(weather_data)
        logging.info("날씨 데이터 Event Hub로 전송 완료")
    else:
        logging.warning("날씨 데이터를 가져오지 못하여 Event Hub로 전송하지 않습니다.")
