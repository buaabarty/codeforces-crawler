import scrapy
from codeforces_crawler.items import CodeforcesCrawlerItem
import time
import csv
from twisted.internet import reactor

item = CodeforcesCrawlerItem()

form_data = {
    'csrf_token': 'cd1407296393164cf9ea14a3c890fe54',
    'action': 'setupSubmissionFilter',
    'frameProblemIndex': 'B',
    'verdictName': 'WRONG_ANSWER',
    'programTypeForInvoker': 'cpp.g++17',
    'comparisonType': 'GREATER_OR_EQUAL',
    'judgedTestCount': '4',
}

class SubmissionsSpider(scrapy.Spider):
    name = "cf_submission"
    allowed_domains = ['codeforces.com']

    # Lựa chọn ngôn ngữ chương trình muốn get về
    wanted_languages = ['GNU C++11']

    # Số lượng tối đa cho mỗi chương trình
    # MAX = 5000
    # count_A = 0
    # count_B = 0
    # count_id = 0

    # Kiểm tra verdict mong muốn
    wanted_verdicts = ['WRONG_ANSWER']

    with open('contest-info.csv', 'r') as f:
        contest_info = []
        header = f.readline()
        for line in f.readlines():
            array = line.split(',')
            contest_id_url = [array[0], array[1]]
            contest_info.append(contest_id_url)

    start_urls = []

    # task_urls = []

    for info in contest_info[0:1]:
        contest_url = info[1]
        contest_id = info[0]
        filename = str(contest_id) + '.csv'
        # with open('crawl-data/contest/' + filename, 'w') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(['submit_id', 'user_name', 'code', 'problem', 'lang', 'verdict', 'contest_id'])
        # task_urls.append(contest_url)
        start_urls.append(contest_url)

    # start_urls.append(task_urls[0])

    # def start_requests(self):
    #     return [scrapy.Request(url=url) for url in self.start_urls]

    def parse(self, response):
        print("=================> Processing: ", response.url)
        submission_id_list = response.xpath('//tr/@data-submission-id').extract()
        print(submission_id_list)
        print('hey')

        for submission_id in submission_id_list:
            print('hey', submission_id)
            # if self.count_A >= self.MAX and self.count_B >= self.MAX:
            #     break

            try:
                submission_user = response.xpath('//tr[@data-submission-id=%s]/td[3]/a/text()' % submission_id)[
                    0].extract().strip()
            except:
                print("False line 65")
                continue

            submission_problem = response.xpath('//tr[@data-submission-id=%s]/td[4]/a/text()' % submission_id)[
                0].extract().strip()

            ###TODO: Processing program count A and B
            print(submission_problem[0])
            if 'D' not in submission_problem[0]:
                continue
            # if 'A' in submission_problem[0] and self.count_A < self.MAX:
            #     self.count_A += 1
            # elif 'B' in submission_problem[0] and self.count_B < self.MAX:
            #     self.count_B += 1
            # else:
            #     continue

            submission_lang = response.xpath('//tr[@data-submission-id=%s]/td[5]/text()' % submission_id)[
                0].extract().strip()
            # Kiểm tra xem có nằm trong các ngôn ngữ mình mong muốn
            if 'C++' not in submission_lang:
                continue

            submission_verdict = response.xpath(
                '//tr[@data-submission-id=%s]/td[6]/span/@submissionverdict' % submission_id)[0].extract().strip()
            print(submission_verdict)
            if submission_verdict not in self.wanted_verdicts:
                continue
            submission_text = response.xpath(
                '//tr[@data-submission-id=%s]/td[6]/span/span/span/text()' % submission_id)[0].extract().strip()
            print('========================')
            print(submission_text)
            if int(submission_text) <= 2 or int(submission_text) > 37:
                continue
            
            code_link = 'https://codeforces.com' + (response.xpath(
                '//tr[@data-submission-id=%s]/td[1]/a[contains(@href, "submission")]/@href' % submission_id)[
                                                        0].extract().strip())

            contest_id = response.xpath('//*[@id="sidebar"]/div[1]/table/tbody/tr[1]/th/a/@href')[0].extract()
            contest_id = contest_id.split('/')[-1]

            time.sleep(0.1)

            yield scrapy.Request(url=code_link, meta={'submission_id': submission_id,
                                                      'submission_user': submission_user,
                                                      'submission_lang': submission_lang,
                                                      'submission_verdict': submission_verdict,
                                                      'submission_problem': submission_problem,
                                                      'contest_id': contest_id
                                                      # 'dont_redirect': True,
                                                      # 'handle_httpstatus_list': [302]
                                                      },
                                 callback=self.parse_code)

        time.sleep(0.1)

        # TODO: generate next-page url
        # if self.count_A >= self.MAX and self.count_B >= self.MAX:
        #     self.count_A = 0
        #     self.count_B = 0
        #     self.count_id += 1
        #     if self.task_urls:
        #         yield scrapy.Request(url=self.task_urls[self.count_id], callback=self.parse)
        #     else:
        #         exit()

        if response.selector.xpath('//span[@class="inactive"]/text()').extract():
            # '\u2192' is the unicode of 'right arrow' symbol
            if response.selector.xpath('//span[@class="inactive"]/text()')[0].extract() != u'\u2192':
                next_page_href = \
                    response.selector.xpath('//div[@class="pagination"]/ul/li/a[@class="arrow"]/@href')[0]
                next_page_url = response.urljoin(next_page_href.extract())
                yield scrapy.Request(next_page_url, callback=self.parse, dont_filter=True)
        else:
            next_page_href = response.selector.xpath('//div[@class="pagination"]/ul/li/a[@class="arrow"]/@href')[1]
            next_page_url = response.urljoin(next_page_href.extract())
            yield scrapy.Request(next_page_url, callback=self.parse, dont_filter=True)

    def parse_code(self, response):
        submission_code = response.xpath('//pre[@id="program-source-text"]/text()').extract()
        # print(source_code)
        item['submission_id'] = response.meta['submission_id']
        item['submission_user'] = response.meta['submission_user']
        item['submission_code'] = submission_code
        item['submission_problem'] = response.meta['submission_problem']
        item['submission_lang'] = response.meta['submission_lang']
        item['submission_verdict'] = response.meta['submission_verdict']
        item['contest_id'] = response.meta['contest_id']
        # print("\n=====================>", self.count_A, self.count_B)

        yield item
