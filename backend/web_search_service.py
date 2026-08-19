from tavily import TavilyClient

class WebSearchService:

    def __init__(self,client):
        self.client = client

    def search_web(self,query: str, max_results: int = 3,top_n:int=3) -> str:
        """
        Tavily API を使用してインターネット検索を行い、要約されたテキストを返します。
        """
        try:
            response = self.client.search(
                query=query,
                search_depth="basic",
                max_results=max_results
            )
            
            # 検索結果（URL、タイトル、コンテンツ）を読みやすいテキストに整形
            results = response.get("results", [])
            if not results:
                return "検索結果が見つかりませんでした。"

            documents = [r.get("content","") for r in results]

            # 最も重要な情報が先頭に並んだ状態で結合して返す
            # for r in results:
            #     snippet = f"タイトル: {r.get('title')}\nURL: {r.get('url')}\n内容: {r.get('content')}"
            #     formatted_snippets.append(snippet)
                
            print("web検索を開始します")
            
            return "\n\n---\n\n".join(documents)
            
        except Exception as e:
            return f"Web検索中にエラーが発生しました: {str(e)}"




