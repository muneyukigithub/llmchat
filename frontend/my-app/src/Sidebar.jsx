import { useState, useEffect, useRef } from 'react';
import { ChevronLeft, ChevronRight, Pencil, MoreHorizontal, Trash2 } from 'lucide-react';

export function Sidebar({ activeThread, setActiveThread }) {
  const [isOpen, setIsOpen] = useState(true);
  const [menuItems, setMenuItems] = useState([]);
  // 初回読み込み完了まで操作させない
  const [isLoading, setIsLoading] = useState(true);
  const [openMenuId, setOpenMenuId] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [editingTitle, setEditingTitle] = useState('');
  const menuRef = useRef(null);

  const handleCreateChat = async (e) => {
    e.preventDefault();
    if (isLoading) return;

    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/chat/create', {
        method: 'POST',
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log(data);

      const newChatThread = {
        thread_id: data.thread_id,
        title: data.title,
      };

      setMenuItems((prev) => [newChatThread, ...prev]);
      setActiveThread(data.thread_id);
    } catch (error) {
      console.error('Failed to create chat:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRename = async (threadId) => {
    const trimmed = editingTitle.trim();
    if (!trimmed) {
      setEditingId(null);
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/v1/chat/threads/${threadId}/title`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ title: trimmed }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      setMenuItems((prev) =>
        prev.map((item) =>
          item.thread_id === threadId ? { ...item, title: trimmed } : item
        )
      );
    } catch (error) {
      console.error('Failed to rename thread:', error);
    } finally {
      setEditingId(null);
      setOpenMenuId(null);
    }
  };

  const handleDelete = async (threadId) => {
    if (!window.confirm('このチャットを削除しますか？')) {
      setOpenMenuId(null);
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/v1/chat/threads/${threadId}`, {
        method: 'DELETE',
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      setMenuItems((prev) => prev.filter((item) => item.thread_id !== threadId));
      if (activeThread === threadId) {
        setActiveThread('');
      }
    } catch (error) {
      console.error('Failed to delete thread:', error);
    } finally {
      setOpenMenuId(null);
    }
  };

  const startRename = (item) => {
    setEditingId(item.thread_id);
    setEditingTitle(item.title);
    setOpenMenuId(null);
  };

  // マウント時に一度だけスレッド一覧を取得する
  useEffect(() => {
    let cancelled = false;

    const fetchThreads = async () => {
      setIsLoading(true);
      try {
        const response = await fetch('http://localhost:8000/api/v1/chat/threads', {
          method: 'GET',
          credentials: 'include',
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (cancelled) return;

        console.log(data);

        const threads = data.map((element) => ({
          thread_id: element.chat_id,
          title: element.title,
        }));
        setMenuItems(threads);
      } catch (error) {
        if (!cancelled) {
          console.error('Failed to fetch threads:', error);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    fetchThreads();

    return () => {
      cancelled = true;
    };
  }, []);

  // メニュー外クリックで閉じる
  useEffect(() => {
    if (!openMenuId) return;

    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setOpenMenuId(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [openMenuId]);

  return (
    <div
      className={`flex flex-col h-screen bg-slate-900 text-white transition-all duration-300 ${
        isOpen ? 'w-64' : 'w-16'
      }`}
    >
      <div className="flex items-center justify-between p-4 border-b border-slate-800">
        {isOpen && <span className="font-bold text-lg">Dashboard</span>}
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="p-1 rounded hover:bg-slate-800 transition-colors ml-auto"
        >
          {isOpen ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
        </button>
      </div>

      <nav className="flex-1 p-2 space-y-1 overflow-y-auto">
        <button
          type="button"
          onClick={handleCreateChat}
          disabled={isLoading}
          className="flex w-full items-center gap-3 p-3 hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Pencil size={20} className="shrink-0" />
          {isOpen && <span>チャットを新規作成</span>}
        </button>

        {isLoading ? (
          <p className="p-3 text-slate-400 text-sm">データ取得中...</p>
        ) : (
          menuItems.map((item) => {
            const thread_id = item.thread_id;
            const isActive = activeThread === thread_id;
            const isEditing = editingId === thread_id;
            const isMenuOpen = openMenuId === thread_id;

            return (
              <div
                key={thread_id}
                className={`group relative flex w-full items-center rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                }`}
              >
                {isEditing ? (
                  <form
                    className="flex-1 min-w-0 p-2"
                    onSubmit={(e) => {
                      e.preventDefault();
                      handleRename(thread_id);
                    }}
                  >
                    <input
                      autoFocus
                      type="text"
                      value={editingTitle}
                      onChange={(e) => setEditingTitle(e.target.value)}
                      onBlur={() => handleRename(thread_id)}
                      onKeyDown={(e) => {
                        if (e.key === 'Escape') {
                          setEditingId(null);
                        }
                      }}
                      className="w-full px-2 py-1 rounded bg-slate-700 text-white text-sm focus:outline-none focus:ring-1 focus:ring-blue-400"
                    />
                  </form>
                ) : (
                  <button
                    type="button"
                    onClick={() => {
                      if (activeThread !== thread_id) {
                        setActiveThread(thread_id);
                      }
                    }}
                    className="flex-1 min-w-0 text-left p-3 truncate"
                  >
                    {isOpen && <span className="truncate block">{item.title}</span>}
                  </button>
                )}

                {isOpen && !isEditing && (
                  <div className="relative shrink-0 pr-1" ref={isMenuOpen ? menuRef : null}>
                    <button
                      type="button"
                      aria-label="メニューを開く"
                      onClick={(e) => {
                        e.stopPropagation();
                        setOpenMenuId(isMenuOpen ? null : thread_id);
                      }}
                      className={`p-1.5 rounded transition-opacity ${
                        isActive
                          ? 'hover:bg-blue-500 text-white'
                          : 'hover:bg-slate-700 text-slate-400 hover:text-white'
                      } ${isMenuOpen ? 'opacity-100' : 'opacity-0 group-hover:opacity-100 focus:opacity-100'}`}
                    >
                      <MoreHorizontal size={16} />
                    </button>

                    {isMenuOpen && (
                      <div className="absolute right-0 top-full mt-1 z-50 w-40 rounded-lg bg-slate-800 border border-slate-700 shadow-lg py-1">
                        <button
                          type="button"
                          onClick={() => startRename(item)}
                          className="flex w-full items-center gap-2 px-3 py-2 text-sm text-slate-200 hover:bg-slate-700"
                        >
                          <Pencil size={14} />
                          タイトルを変更
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDelete(thread_id)}
                          className="flex w-full items-center gap-2 px-3 py-2 text-sm text-red-400 hover:bg-slate-700"
                        >
                          <Trash2 size={14} />
                          削除
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </nav>
    </div>
  );
}
