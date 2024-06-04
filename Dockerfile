FROM rocker/shiny
LABEL maintainer="maxblasdel@gmail.com"

RUN sed -i '1ipython /usr/bin/python3;' /etc/shiny-server/shiny-server.conf 
# RUN chown app:app -R /home/app
# USER app
# EXPOSE 3838
# CMD ["R", "-e", "shiny::runApp('/home/app')"]