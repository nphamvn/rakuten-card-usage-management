FROM python:3.9

ENV DEBIAN_FRONTEND=noninteractive
ENV GECKODRIVER_VER=v0.30.0
ENV FIREFOX_VER=87.0
ENV PYTHONIOENCODING=utf-8
ENV TZ="Asia/Tokyo"
ENV LANG=C.UTF-8
ENV LANGUAGE=en_US:en

RUN apt update && apt install -y firefox-esr

WORKDIR /tmp
RUN wget https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VER}/geckodriver-${GECKODRIVER_VER}-linux64.tar.gz
RUN tar zxvf geckodriver-${GECKODRIVER_VER}-linux64.tar.gz
RUN chmod +x geckodriver
RUN mv geckodriver /usr/bin/geckodriver
RUN rm -rf geckodriver-${GECKODRIVER_VER}-linux64.tar.gz

RUN apt install -y libx11-xcb1 libdbus-glib-1-2 \
  && curl -sSLO https://download-installer.cdn.mozilla.net/pub/firefox/releases/${FIREFOX_VER}/linux-x86_64/en-US/firefox-${FIREFOX_VER}.tar.bz2 \
  && tar -jxf firefox-* \
  && mv firefox /opt/ \
  && chmod 755 /opt/firefox \
  && chmod 755 /opt/firefox/firefox \
  && rm -f firefox-${FIREFOX_VER}.tar.bz2

RUN wget https://noto-website-2.storage.googleapis.com/pkgs/Noto-hinted.zip && unzip Noto-hinted.zip \
  && mkdir -p /usr/share/fonts/opentype/noto \
  && rm -f README LICENSE_OFL.txt \
  && mv *.otf *.ttf /usr/share/fonts/opentype/noto \
  && fc-cache -f -v \
  && rm Noto-hinted.zip

RUN mkdir -p /app
ADD requirements.txt /app/requirements.txt
ADD main.py /app/main.py

WORKDIR /app
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

CMD ["python3", "main.py"]