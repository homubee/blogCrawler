# blogCrawler
## Description
블로그 내의 텍스트를 크롤링하는 프로그램

## Stack
<div align=center>
  <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/vscode-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white">
  <img src="https://img.shields.io/badge/git-F05032?style=for-the-badge&logo=git&logoColor=white">
  <img src="https://img.shields.io/badge/github-181717?style=for-the-badge&logo=github&logoColor=white">
</div>

## Environment
- python 3.7.6
- beautifulsoup4 4.9.3

## Run

### Dependencies

    pip install beautifulsoup4

### Main

    python blogCrawler.py
    크롤링할 주소를 입력 : [blog url]

    ... (crawled result will be printed here) ...

    저장할 경로를 입력 (입력하지 않으면 현재 경로에 생성됩니다.) : [save directory path]
    제목 머리글 입력 (입력하지 않으면 머리글 없이 생성됩니다.): [title prefix]
    본 게시글이 포함된 카테고리 전체를 크롤링할까요? (Y/N) : [Y/N]

    ... (crawling process will be printed here) ...

## Functionality
- 네이버 블로그 텍스트 크롤링 기능
  - 블로그 제목 및 내용 크롤링
  - 블로그 내의 p태그에 포함된 텍스트만 크롤링 가능
- 네이버 블로그 카테고리 전체 크롤링 기능
  - 현재 크롤링한 게시글의 카테고리 내의 게시글 전체 크롤링 가능
- 네이버 블로그 유효 URL 체크 기능
  - 네이버 블로그 URL 패턴에 따라 유효성을 판단
  - 모바일 URL은 유효한 URL로 판단하지 않음
