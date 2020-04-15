import scrapy


# c1d19424297a1c7ccdc72e485a4df1632d08

class PorjSpider(scrapy.Spider):
    name = "proj"
    user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
    allowed_domains = ["eutils.ncbi.nlm.nih.gov"]
    start_urls = [
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&api_key=c1d19424297a1c7ccdc72e485a4df1632d08&term=orthodontic&retmax=70000&usehistory=y"]

    def parse(self, response):
        programs = response.xpath('//Id/text()').extract()
        for program in programs:
            # parse article info
            info_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=" + program + "&retmode=xml"
            yield scrapy.Request(info_url, callback=self.parse_data)

    def parse_data(self, response):
        data = {}
        pmid = response.xpath('//ArticleId[@IdType="pubmed"]/text()').extract()
        if len(pmid) == 0:
            pmid = [""]
        data["pmid"] = pmid[0]
        doi = response.xpath('//ArticleId[@IdType="doi"]/text()').extract()
        if len(doi) == 0:
            doi = [""]
        data["doi"] = doi[0]
        year = response.xpath('//PubDate/Year/text()').extract()
        month = response.xpath('//PubDate/Month/text()').extract()
        day = response.xpath('//PubDate/Day/text()').extract()
        if len(year) == 0:
            year = [""]
        if len(month) == 0:
            month = [""]
        if len(day) == 0:
            day = [""]
        data["date"] = "-".join((year[0], month[0], day[0]))
        title = response.xpath('//ArticleTitle/text()').extract()
        if len(title) == 0:
            title = [""]
        data["title"] = title[0]
        data["abstract"] = '\n'.join((record for record in response.xpath('//AbstractText/text()').extract()))
        last_names = response.xpath('//LastName/text()').extract()
        first_names = response.xpath('//ForeName/text()').extract()
        names = (last_names[i] + ', ' + first_names[i] for i in range(len(last_names)))
        data["authors"] = names
        text_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&api_key=c1d19424297a1c7ccdc72e485a4df1632d08&id=" + \
                   data["pmid"] + "&cmd=prlinks"
        full_data = scrapy.Request(text_url, meta={"info": data}, callback=self.parse_full_text)
        yield full_data

    def parse_full_text(self, response):
        link = response.meta["info"]
        url_list = response.xpath('//ObjUrl/Url/text()').extract()
        if len(url_list) == 0:
            link["url"] = ""
        else:
            link["url"] = str(url_list[0])
        yield link
# /div[@class="collapsible-content"]/div[@class="line"]/span[@class="text"]/text()
