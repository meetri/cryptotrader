# cryptotrader
a crypto scraper and bot trader

*Warning:* This is a toy. This is only a toy. 
requires a bit to get it running. I added a dockerfile and swarm compose configs to simplify things

*Dependencies*
- postgres
- influxdb
- grafana
See docker swarm-mode compose configs.

I basically run my bot in a tmux session on the cloud somewhere. Currently it outputs directly to the terminal. 
( see screenshot )

TODO:
- [x] build scraper to gather data into influxdb for visualization in grafana
- [x] build TA framework using TA-lib and log in influxdb for visualization in grafana
- [x] build bots to respond to TA analysis
- [x] build trade management system to keep track of and manage trades ( work-in-progress )
- [x] add dockerfile and docker compose for dependencies
- [x] add db schema and skeleton data to repo
- [ ] clean up code ( lots of old code needs to be removed... )
- [ ] create setup script
- [ ] log trade triggers in influxdb to be visualized in grafana
- [ ] create a simpler datasource that will poll live exchange API data real-time ( used for 1hr candles and up )


*Donations Welcome*
1H1pzUTYbkEZqTJ2Gk2YBAURoL95U3nW7s
