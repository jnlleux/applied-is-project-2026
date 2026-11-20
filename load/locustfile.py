from locust import HttpUser, task, between

class CatalogUser(HttpUser):
    wait_time = between(0.1, 0.5)
    @task(3)
    def cars(self):
        self.client.get('/cars', name='GET cars')
    @task(2)
    def categories(self):
        self.client.get('/categories', name='GET categories')
    @task
    def search(self):
        self.client.get('/cars?search=Toyota&min_price=10000', name='GET filtered cars')
