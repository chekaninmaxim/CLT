CLT (Central limit theorem)
=================================================================================================================

### Discleimer!
Проект створено з навчальною метою, аби отримати розуміння як піднімати складні real-time системи, та запускати spark-streaming додатки. Тому методи, використані тут, не у всіх випадках є добрим прикладом рішення подібних задач у реальному житті 

### Данний проект слакдається з таких компонентів:

 - Кафка кластер -
 - Генератор рандомних чисел. python script random_data_generator (Генерує рандомні числа і надсилає їх в кафку topic: random_numbers)
 - Спарк аплікейшин, який отримує данні з Кафки, з топіку random_numbers, обробляє мікробатчі, рахуючи середнє значення кожного мікробатчу, та кладе результат в Hive таблицю з назвою batch_mean_and_size
 - Hive база данних з назвою test1, яка використовує HDFS для зберігання та postgresql, в якості metastore. 
 - Веб додаток, який візуалізує данні, отримані з хайв таблиці, використовуючи бібліотеку streamlite.

Всі компоненти та сервіси, окрім random_data_generator запускаються в докер контейнерах *див. файл docker-compose.yml*

## Інструкція з запуску всіх сервісів.

### Перед запуском слід переконатись, що на робочій машині у вас встановлено:
 - Docker https://docs.docker.com/desktop/install/windows-install/ Якщо у вас Windows то обирайте WSL2 backend
 - Python 3.11 та pycharm
 - Java 8, та Spark (Якщо не плануєте експериментувати із Scala Spark, то цей пункт не обов'язковий)
 - Windows термінал https://apps.microsoft.com/detail/9N0DX20HK701?launch=true&mode=full&referrer=bingwebsearch&ocid=bingwebsearch&hl=en-us&gl=US (дуже полегшує роботу із запуском команд, оскільки має деякі linux фічі, теж не обов'язково)
 

**Перед виконанням всіх кроків відкрийте папку CLT в cmd або windows terminal або просто в терміналі, якщо ви на лінуксі**

### Крок 1. Збираємо образ для спарк мастер ноди та воркер ноди

Заходимо в папку CLT/docker_cluster/spark_node_image 
```
cd docker_cluster/spark_node_image/
```

В папці CLT/docker_cluster/spark_node_image виконуємо команду:
```
docker build -t cluster-apache-spark .
```

### Крок 2. Збираємо образ веб додатку для візуалізаціїї данних

Переходимо в папку docker_cluster/visualization_app

```
cd  ../visualization_app
```

В папці visualization_app виконуємо команду:

```
docker build -t  streamlit-data-vis .
```

### Крок 3. Запускаємо всі контейнери за допомогою *docker compose*

Переходимо в папку docker_cluster
```
cd ..
```

В папці docker_cluster виконуємо команду:

``` 
docker compose up -d
```

Чекаємо поки всі 10 контейнерів піднімуться.
З веб-браузеру можна перевірити чи вже піднялись деякі сервіси, наприклад:
localhost:50070 - namenode hdfs
localhost:9090 - spark master node
localhost:8501 - веб додаток для візуалізації данних

### Крок 4. Створюємо нову базу з назвою test1 в хайві

Відкриваємо нове вікно Терміналу
В новому вікні терміналу виконуємо команду
``` 
docker exec -it docker_cluster-hive-server-1 sh
```

В результаті маємо опинитись в середині контейнура з хайвом. В хайв контейнері заходимо в hive shel виконавши команду:
```
hive
```

В хайв шелі віконуємо команду 

```
CREATE DATABASE IF NOT EXISTS test1;
```

Виходимо з хайву і контейнеру натисканням клавіш ctrl + D

### Крок 5. Запускаємо спарк або пайспарк додатки

Відкриваємо нове вікно терміналу та виконуємо команду:
```
docker exec -it docker_cluster-spark-master-1 sh
```

Коли зайшли в shel конейнера, в шелі контейнера виконуємо команду:

```
/opt/spark/bin/spark-submit --master spark://spark-master:7077 --total-executor-cores 1  --driver-memory 1G  --executor-memory 1G  --class Main --name spark_microbatch_processor --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.2,org.apache.spark:spark-streaming_2.12:3.0.2,org.apache.kafka:kafka-clients:3.0.2  /opt/spark-apps/spark_app.jar
``` 

Якщо хочем запустити pyspark додаток, то виконуємо команду:

```
/opt/spark/bin/spark-submit --master spark://spark-master:7077 --total-executor-cores 1  --driver-memory 1G  --executor-memory 1G  --class Main --name spark_microbatch_processor --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.2,org.apache.spark:spark-streaming_2.12:3.0.2,org.apache.kafka:kafka-clients:3.0.2  /opt/spark-apps/pyspark_app.py
```

Чекаємо поки запуститься...

Якщо подивитись, як описаний контейнер із spark-master, то можна побачити, що там є bind mount папки docker_cluster/spark_apps в папку  /opt/spark-apps/ це означає, що spark-master контейнер бачитиме всі файли, які ми покладемо в папку docker_cluster/spark_apps.
Це дозволяє нам змінювати код на нашій машині і легко передавати цей код у вигляді файлів .py (у випадку pyspark) або .jar (у випадку java або scala) в контейнер, для подальшого запуску. Зараз там є файли pyspark_app.py та spark_app.jar, але можуть бути будь-які ваші файли. Для експериментів є проект на scala micro_batch_processor, де можна знайти код, який було скомпільовано в файл spark_app.jar. Також є pyspark версія pyspark_microbatch_processor аналогічний проект написаний на python.


### Крок 6. Запускаємо генератор рандомних чисел локально
Можна запустити через pycharm або виконати наступні кроки:
Відкриваємо ще одне вікно терміналу:
Заходимо в папку CLT/random_data_generator

Виконуємо команду 
```
./venv/Scripts/activate
```

Встановлюємо модуль python-kafka

```
 pip install python-kafka
```

Запускаємо скріпт main.py:

```
python main.py
```
(В залежності від налаштувань в декого може спрацювати команда python3 замість python)


### Крок 7. Відкриваємо веб додоток у браузері 
Відкриваємо localhost:8501 та дивимось як гістограма стає все більше і більше схожою на гаусовий розподіл (або ні)





 