# Sea Temp Scraper

Grab daily Adriatic sea temps for fun.

* `sea_temp_scraper.py` – pulls today’s DHMZ table and appends to `sea_temps.csv` (cron it at 18:00 if you like).
* `sea_temp_plot.py` – reads the CSV and spits out line plots (all stations or one you name).

Source table: [https://meteo.hr/podaci.php?section=podaci\_vrijeme\&param=more\_n](https://meteo.hr/podaci.php?section=podaci_vrijeme&param=more_n)
Station map: [https://meteo.hr/infrastruktura.php?section=mreze\_postaja\&param=pmm\&el=tmore](https://meteo.hr/infrastruktura.php?section=mreze_postaja&param=pmm&el=tmore)

