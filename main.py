import schedule
import time
from Parsing.citilink_smartphone import citilink
from Parsing.dns_smartphone import dns
from Parsing.mvideo_smartphone import mvideo
from SearchBot.buyphone import start_bot
import multiprocessing


def pars():
    # schedule.every(10).seconds.do(citilink)
    schedule.every(10).minutes.do(mvideo)
    schedule.every(10).minutes.do(citilink)
    schedule.every(10).minutes.do(dns)
    # schedule.every(6).hour.do()

    while True:
        schedule.run_pending()
        time.sleep(1)


def main():
    p1 = multiprocessing.Process(target=start_bot)
    p2 = multiprocessing.Process(target=pars)
    p1.start()
    p2.start()


if __name__ == '__main__':
    # freeze_support() here if program needs to be frozen
    main()
