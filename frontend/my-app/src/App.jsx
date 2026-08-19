import { useState, useEffect, useRef } from 'react';
import { Sidebar } from './Sidebar';

export function App() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [activeThread, setActiveThread] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const answerAreaRef = useRef(null);

 

  const getMessages = async() => {
    if (!activeThread) return;

    const response = await fetch('http://localhost:8000/api/v1/chat/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ thread_id: activeThread }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log(data);
    console.log(activeThread)
    const contents = data;
    setMessages(contents);

  }

   // スレッド切替時は表示をリセット（別スレッドの履歴が混ざらないように）
   useEffect(() => {
    setMessages([]);
    setQuery('');
    getMessages();
  }, [activeThread]);

  // 新しいメッセージが追加・更新されたら下端へスクロール
  useEffect(() => {
    const el = answerAreaRef.current;
    if (el) {
      el.scrollTop = el.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const prompt = query.trim();
    if (!prompt || isLoading) return;
    if (!activeThread) {
      setMessages((prev) => [
        ...prev,
        { role: 'model', content: '先にサイドバーからチャットを選択または作成してください。' },
      ]);
      return;
    }

    setIsLoading(true);
    setQuery('');
    setMessages((prev) => [
      ...prev,
      { role: 'user', content: prompt },
      { role: 'model', content: '' },
    ]);

    try {
      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ prompt, thread_id: activeThread }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setMessages((prev) => {
        const next = [...prev];
        const last = next[next.length - 1];
        next[next.length - 1] = {
          ...last,
          content: data.value ?? '',
        };
        return next;
      });
    } catch (error) {
      console.error('Chat error:', error);
      setMessages((prev) => {
        const next = [...prev];
        const last = next[next.length - 1];
        next[next.length - 1] = {
          ...last,
          content: (last.content || '') + '\n[エラーが発生しました]',
        };
        return next;
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50 text-slate-800">
      <Sidebar activeThread={activeThread} setActiveThread={setActiveThread} />

      <main className="flex-1 flex flex-col h-full overflow-y-auto p-8">
        <div className="max-w-4xl w-full mx-auto flex flex-col h-full gap-6">
          <h2 className="text-2xl font-bold text-slate-800">LLMチャット</h2>

          <div
            id="answer-area"
            ref={answerAreaRef}
            className="flex-1 p-6 rounded-xl border border-slate-200 bg-white shadow-sm overflow-y-auto"
          >
            {messages.length === 0 ? (
              <span className="text-slate-400">
                {isLoading ? '思考中...' : 'ここに会話が表示されます'}
              </span>
            ) : (
              <div className="flex flex-col gap-4">
                {messages.map((message, index) => {
                  const isUser = message.role === 'user';
                  const isEmptyAssistant =
                    message.role === 'model' && !message.content && isLoading;

                  return (
                    <div
                      key={`${message.role}-${index}`}
                      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[85%] rounded-xl px-4 py-3 whitespace-pre-wrap leading-relaxed ${
                          isUser
                            ? 'bg-blue-600 text-white'
                            : 'bg-slate-100 text-slate-800'
                        }`}
                      >
                        {isEmptyAssistant ? '思考中...' : message.content}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="質問を入力してください..."
              disabled={isLoading}
              className="flex-1 px-4 py-3 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100 disabled:cursor-not-allowed transition-all"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors shrink-0"
            >
              {isLoading ? '送信中...' : '送信'}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}

export default App;
