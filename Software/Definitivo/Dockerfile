FROM python:3.8
ADD MyMQTT.py /   
ADD main.py / 
ADD settings.json / 
ADD Bot.py / 
ADD BT_control.py / 
ADD Catalog.py / 
ADD Device_Connector.py / 
ADD HR_control.py / 
ADD OX_control.py / 
ADD RT_control.py / 
ADD Thingspeak_adaptor.py / 
ADD WebManager.py / 
ADD Window.py / 
ADD Catalog.py / 
ADD WebManager.py /
ADD requirements.txt /
ADD Catalog.json / 
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
CMD ["python3","./main.py"]
CMD ["python3","./Device_Connector.py"] 
CMD ["python3","./Thingspeak_adaptor.py"] 
CMD ["python3","./Bot.py"] 
CMD ["python3","./BT_control.py"] 
CMD ["python3","./CentralHeating.py"] 
CMD ["python3","./HR_control.py"] 
CMD ["python3","./OX_control.py"] 
CMD ["python3","./RT_control.py"] 
CMD ["python3","./Window.py"] 