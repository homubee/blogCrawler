import re
import os
import requests
from bs4 import BeautifulSoup


def writeFile(file, string):
    """
    파일 입력 함수

    끝에 \\n 문자 포함하여 입력하도록 기능 추가
    """

    file.write(string + "\n")


class NaverBlogCrawler:
    """
    네이버 블로그 크롤러 클래스
    """

    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}

    def __init__(self, url):
        """
        생성자
        """

        # Blog data
        self.blodId = None
        self.logNo = None
        self.categoryNo = None

        # set url
        self.inputURL = url
        self.setURL(self.inputURL)

        # Response & BeautifulSoup data
        self.initResponse = None
        self.initSoup = None
        self.iframeSrc = None
        self.iframeResponse = None
        self.iframeSoup = None

        self.htmlTitle = None
        self.divSoup = None

    def standardizeURL(self):
        """
        URL 표준화 함수

        표준화 성공, 실패를 불 값으로 리턴함
        
        잘못된 URL 체크함(기본 구조가 올바른지만 체크)

        블로그 아이디 및 로그 넘버 초기화
        """

        isValid = True

        # 네이버 블로그 도메인 체크
        if self.inputURL[:22] == "https://blog.naver.com":
            
            # 쿼리문 포함 여부 체크
            if "?" in self.inputURL:
                print("쿼리문 포함")
                # blogId parameter 포함 여부 체크
                self.blodId = self.inputURL.find("blogId")
                if self.blodId == -1:
                    isValid = False
                else:
                    self.blodId = self.inputURL[self.blodId+7 : self.inputURL.find("&")]
                    print(self.blodId)
                    # logNo parameter 포함 여부 체크
                    self.logNo = self.inputURL.find("logNo")
                    if self.logNo == -1:
                        isValid = False
                    else:
                        self.logNo = self.inputURL[self.logNo+6 : self.logNo+6 + self.inputURL[self.logNo+6:].find("&")]
                        print(self.logNo)
                        self.inputURL = self.inputURL[:22] + "/" + self.blodId + "/" + self.logNo
                        print(self.inputURL)
            else:
                # url 형식 체크
                if (len(self.inputURL.split("/")) < 5):
                    isValid = False
                else:
                    self.blodId = self.inputURL.split("/")[3]
                    self.logNo = self.inputURL.split("/")[4]
                    # 내용이 없는지 체크
                    if ((self.blodId == "") | (self.logNo == "")):
                        isValid = False

        if isValid:
            print("올바른 주소입니다.")
            return True
        else:
            print("올바르지 않은 주소이거나 네이버 블로그 주소가 아닙니다.")
            self.inputURL = None
            return False
    
    def setURL(self, url):
        """
        URL 설정 함수

        inputURL 초기화하고 표준화 및 결과 리턴
        """

        self.inputURL = url
        return self.standardizeURL()
    
    def validityCheck(self):
        """
        유효성 체크

        inputURL이 None인지 체크 및 Exception 발생
        """

        if self.inputURL == None:
            raise Exception("URL 설정 필요")
    
    def setBeautifulSoup(self):
        """
        Response & BeautifulSoup 설정 함수

        필요한 요소를 추출하여 Response & BeautifulSoup 초기화
        """

        self.validityCheck()
        self.initResponse = requests.get(self.inputURL)
        # request를 통해 받아온 response의 status code 체크
        if self.initResponse.status_code >= 300:
            raise Exception("Response 실패\nStatus code : " + str(self.initResponse.status_code))
        self.initSoup = BeautifulSoup(self.initResponse.content, "html.parser")
        #iframe 내의 주소로 접근하여 프레임 내부 html을 추출
        self.iframeSrc = self.initSoup.iframe["src"]
        self.iframeResponse = requests.get("https://blog.naver.com/" + self.iframeSrc, headers=NaverBlogCrawler.headers)
        self.iframeSoup = BeautifulSoup(self.iframeResponse.text.replace("<br>", "\n"), "html.parser")
    
    
    def parsePage(self):
        """
        본문 내용 파싱 함수

        각 에디터 버전에 따라 html 문서 구조가 다르기 때문에 구별하여 파싱 (제목으로 구별함)

        카테고리 넘버도 이때 수집됨
        """

        self.validityCheck()
        # 스마트 에디터 ONE
        if self.iframeSoup.find("div", attrs={"class":"se-module se-module-text se-title-text"}):
            self.htmlTitle = self.iframeSoup.find("div", attrs={"class":"se-module se-module-text se-title-text"})
            self.divSoup = self.iframeSoup.find_all("div", attrs={"class":"se-main-container"})
        # 스마트 에디터 2.0
        elif self.iframeSoup.find("div", attrs={"class":"htitle"}):
            self.htmlTitle = self.iframeSoup.find("div", attrs={"class":"htitle"})
            self.htmlTitle = self.htmlTitle.find_all("span")[0]
            self.divSoup = self.iframeSoup.find_all("div", attrs={"id":"postViewArea"})
        # 스마트 에디터 3.0으로 추정...
        # 줄바꿈 형식이 <br>로 되어 있음, 크롤링할 경우, 양식이 흐트러지는 문제 발생
        # 처음 소스를 가져올 때, <br> 태그를 모두 \n으로 치환하여 가져오는 방식으로 해결
        elif self.iframeSoup.find("div", attrs={"class":"se_editArea"}):
            self.htmlTitle = self.iframeSoup.find("div", attrs={"class":"se_editArea"})
            self.divSoup = self.iframeSoup.find_all("div", attrs={"class":"se_component_wrap sect_dsc __se_component_area"})
        else:
            raise Exception("스마트 에디터 ONE/2.0/3.0 이 아닙니다.")

        categorySoup = self.iframeSoup.find("div", attrs={"class":"wrap_title"})
        categorySoup = categorySoup.a["href"]

        # 카테고리 번호 추출
        self.categoryNo = categorySoup.find("categoryNo")
        self.categoryNo = categorySoup[self.categoryNo+11 : self.categoryNo+11 + categorySoup[self.categoryNo+11:].find("&")]
    
    
    def print(self):
        """
        출력 함수

        본문 내용 콘솔에 출력

        본문 div 내의 p 태그 전체를 긁어와서 내부 텍스트만 추출
        """

        self.validityCheck()
        print("사이트 명 : " + self.initSoup.title.string)
        print("제목 : " + self.iframeSoup.title.string)
        print(self.htmlTitle.get_text())
        for paragraph in self.divSoup:
            paragraphList = paragraph.find_all("p")
            for text in paragraphList:
                print(text.get_text())
                print("\n")
    
    
    def write(self, path = ".", titleHeader = ""):
        """
        파일 입력 함수

        파일명 : 머릿글 + 게시글 제목 (일부 특수 문자 제외 처리)

        내용 : 게시글 제목 + 줄바꿈 * 2 + 본문
        """

        self.validityCheck()
        # crawl directory 생성(이미 있다면 패스)
        if not(os.path.isdir(path + "\\crawl")):
            os.mkdir(path + "\\crawl")
        
        fileName = self.htmlTitle.get_text()
        title = self.htmlTitle.get_text()
        # 파일명 특수 문자 제외 처리
        fileName = re.sub('[\\/:*?"<>|\n]','',fileName)
        # 제목 줄바꿈 제외 처리
        title = re.sub('[\n]','',title)
        # 파일명/제목 끝에 공백 문자 붙으면 지저분하므로 정리
        # 파일명 끝에 .도 정리
        while True:
            if fileName[-1] == " ":
                fileName = fileName[:-1]
            if title[-1] == " ":
                title = title[:-1]
            else:
                if fileName[-1] == ".":
                    fileName = fileName[:-1]
                else:
                    break
        
        # 머릿글 처리
        if titleHeader == "":
            file = open(path + "\\crawl\\" + fileName + ".txt", "wt", encoding = "UTF-8")
        else:
            file = open(path + "\\crawl\\" + titleHeader + fileName + ".txt", "wt", encoding = "UTF-8")
        
        writeFile(file, title)
        writeFile(file, "\n")

        # p 태그를 찾아 한줄씩 파일에 저장한다.
        for paragraph in self.divSoup:
            paragraphList = paragraph.find_all("p")
            for text in paragraphList:
                writeFile(file, text.get_text())

        file.close()

    def crawlAll(self, path = ".", titleHeader = "", isNumberHead = False):
        """
        카테고리 내 게시글 전체 크롤링

        위쪽에 있는 카테고리 게시글 목록에서 가져오는 방식

        https://blog.naver.com/PostTitleListAsync.naver?blogId=[블로그id]&currentPage=[게시글번호]&categoryNo=[카테고리번호]
        """
        
        crawler = NaverBlogCrawler(self.inputURL)
        crawler.setBeautifulSoup()
        crawler.parsePage()
        
        pageNo = 1
        prevPostList = None

        # 그냥 소스를 긁어와서는 내용을 찾을 수가 없음
        # 네이버에 카테고리 게시글 목록 보는 레이아웃이 2개 있는데, 아래쪽 카테고리 게시글 목록은 버그가 발생, 따라서 위쪽을 긁어오는 방식으로 구현함
        # 번호 부여 여부에 따라 먼저 카운팅하여 전체 개수를 확인(가장 최신글부터 크롤링하므로 인덱스 붙이려면 전체 개수를 알아야 함)
        count = 0
        if isNumberHead:
            while True:
                print("https://blog.naver.com/PostTitleListAsync.naver?blogId="+crawler.blodId+"&currentPage="+str(pageNo)+"&categoryNo="+crawler.categoryNo+"&countPerPage=30")
                postList = requests.get("https://blog.naver.com/PostTitleListAsync.naver?blogId="+crawler.blodId+"&currentPage="+str(pageNo)+"&categoryNo="+crawler.categoryNo+"&countPerPage=30").text
                postList = postList[postList.find("tagQueryString")+24:-2]
                postList = postList.split("&logNo=")
                # 더이상 카테고리 게시글 목록이 넘어가지 않을 때까지 반복, 네이버 시스템 상 max 이상 넘어가면 max 값을 리턴해줌
                if (prevPostList == postList):
                    break
                for i in postList:
                    count += 1
                pageNo += 1
                prevPostList = postList
        
        pageNo = 1
        prevPostList = None

        while True:
            print("https://blog.naver.com/PostTitleListAsync.naver?blogId="+crawler.blodId+"&currentPage="+str(pageNo)+"&categoryNo="+crawler.categoryNo+"&countPerPage=30")
            postList = requests.get("https://blog.naver.com/PostTitleListAsync.naver?blogId="+crawler.blodId+"&currentPage="+str(pageNo)+"&categoryNo="+crawler.categoryNo+"&countPerPage=30").text
            postList = postList[postList.find("tagQueryString")+24:-2]
            postList = postList.split("&logNo=")
            # 더이상 카테고리 게시글 목록이 넘어가지 않을 때까지 반복, 네이버 시스템 상 max 이상 넘어가면 max 값을 리턴해줌
            if (prevPostList == postList):
                break
            print(postList)
            for i in postList:
                inputURL = "https://blog.naver.com/" + crawler.blodId + "/" + str(i)
                print(inputURL)
                crawler.setURL(inputURL)
                try:
                    crawler.setBeautifulSoup()
                    crawler.parsePage()
                    if isNumberHead:
                        crawler.write(path, str(count) + ". " + titleHeader)
                        count -= 1
                    else:
                        crawler.write(path, titleHeader)
                except Exception as e:
                    print(e)
            pageNo += 1
            prevPostList = postList


# main
if __name__ == "__main__":
    inputURL = input("크롤링할 주소를 입력 : ")
    crawler = NaverBlogCrawler(inputURL)
    try:
        crawler.setBeautifulSoup()
        crawler.parsePage()
        crawler.print()
        inputPath = input("저장할 경로를 입력 (입력하지 않으면 현재 경로에 생성됩니다.) : ")
        inputTitle = input("제목 머리글 입력 (입력하지 않으면 머리글 없이 생성됩니다.): ")
        if inputPath == "":
            inputPath = "."
        
        isCategory = input("본 게시글이 포함된 카테고리 전체를 크롤링할까요? (Y/N) : ")

        if isCategory == "Y" or isCategory == "y":

            isNumberHead = input("게시글 순서에 따라 숫자를 추가할까요? (Y/N) : ")

            if isNumberHead == "Y" or isNumberHead == "y":
                isNumberHead = True
            else:
                isNumberHead = False
            crawler.crawlAll(inputPath, inputTitle, isNumberHead)

            
        else:
            crawler.write(inputPath, inputTitle)
        
    except Exception as e:
        print(e)
    
