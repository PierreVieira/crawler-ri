from datetime import time
from urllib import robotparser
from util.threads import synchronized
from collections import OrderedDict
from .domain import Domain


class Scheduler():
    # tempo (em segundos) entre as requisições
    TIME_LIMIT_BETWEEN_REQUESTS = 20

    def __init__(self, str_usr_agent, int_page_limit, int_depth_limit, arr_urls_seeds):
        """
            Inicializa o escalonador. Atributos:
                - `str_usr_agent`: Nome do `User agent`. Usualmente, é o nome do navegador, em nosso caso,  será o nome do coletor (usualmente, terminado em `bot`)
                - `int_page_limit`: Número de páginas a serem coletadas
                - `int_depth_limit`: Profundidade máxima a ser coletada
                - `int_page_count`: Quantidade de página já coletada
                - `dic_url_per_domain`: Fila de URLs por domínio (explicado anteriormente)
                - `set_discovered_urls`: Conjunto de URLs descobertas, ou seja, que foi extraída em algum HTML e já adicionadas na fila - mesmo se já ela foi retirada da fila. A URL armazenada deve ser uma string.
                - `dic_robots_per_domain`: Dicionário armazenando, para cada domínio, o objeto representando as regras obtidas no `robots.txt`
        """
        self.str_usr_agent = str_usr_agent
        self.int_page_limit = int_page_limit
        self.int_depth_limit = int_depth_limit
        self.int_page_count = 0

        self.dic_url_per_domain = OrderedDict()
        self.set_discovered_urls = set()
        self.dic_robots_per_domain = {}

    @synchronized
    def count_fetched_page(self):
        """
            Contabiliza o número de paginas já coletadas
        """
        self.int_page_count += 1

    def has_finished_crawl(self):
        """
            Verifica se finalizou a coleta
        """
        if(self.int_page_count > self.int_page_limit):
            return True
        return False

    @synchronized
    def can_add_page(self, obj_url, int_depth):
        """
            Retorna verdadeiro caso  profundidade for menor que a maxima
            e a url não foi descoberta ainda
        """
        if (self.int_depth_limit <= int_depth or obj_url.geturl() in self.dic_url_per_domain):
            return False

        return True

    @synchronized
    def add_new_page(self, obj_url, int_depth):
        """
            Adiciona uma nova página
            obj_url: Objeto da classe ParseResult com a URL a ser adicionada
            int_depth: Profundidade na qual foi coletada essa URL
        """
        # https://docs.python.org/3/library/urllib.parse.html

        if (not self.can_add_page(obj_url, int_depth)):
            return False

        # if (obj_url.geturl() not in self.dic_url_per_domain):
        #     self.dic_url_per_domain[obj_url.geturl()] = []

        self.dic_url_per_domain[obj_url.geturl()] = [(obj_url, int_depth)]
        self.set_discovered_urls.add(obj_url.geturl())

        # self.dic_url_per_domain = OrderedDict(
        #     sorted(self.dic_url_per_domain.items(), key=lambda t: t[0]))

        return True

    @synchronized
    def get_next_url(self):
        """
        Obtêm uma nova URL por meio da fila. Essa URL é removida da fila.
        Logo após, caso o servidor não tenha mais URLs, o mesmo também é removido.
        """
        for domain, urls in self.dic_url_per_domain.items():
            if (self.dic_url_per_domain[domain] == []):
                del self.dic_url_per_domain[domain]
            else:
                for url in urls:
                    self.dic_url_per_domain[domain].pop()
                    return url

        # time.sleep(1)
        # return self.get_next_url()

    def can_fetch_page(self, obj_url):
        """
        Verifica, por meio do robots.txt se uma determinada URL pode ser coletada
        """

        return False
