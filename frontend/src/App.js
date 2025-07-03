import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  DndContext,
  PointerSensor,
  useSensor,
  useSensors,
  useDroppable,
} from '@dnd-kit/core';
import {
  SortableContext,
  verticalListSortingStrategy,
  useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import LoginForm from './components/LoginForm';
import { pointerWithin } from '@dnd-kit/core';

axios.defaults.withCredentials = true;
const API_BASE_URL = process.env.REACT_APP_API_URL || '';

function SortableItem({ id, content, priority, tags, dueDate, assignedTo, containerId }) {
  tags = Array.isArray(tags) ? tags : [];
  const assignedUser = Array.isArray(assignedTo) && assignedTo.length > 0;

  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id, data: { containerId } });

  const priorityColors = {
    low: '#5cb85c',
    medium: '#f0ad4e',
    high: '#d9534f',
  };

  let countdown = '';
  let expired = false;
  if (dueDate) {
    const now = new Date();
    const deadline = new Date(dueDate);
    const diff = deadline - now;
    expired = diff < 0;
    const days = Math.abs(Math.floor(diff / (1000 * 60 * 60 * 24)));
    const hours = Math.abs(Math.floor((diff / (1000 * 60 * 60)) % 24));
    countdown = expired
      ? `⛔ Vencida hace ${days}d ${hours}h`
      : `🕒 ${days}d ${hours}h restantes`;
  }

  const style = {
    transform: CSS.Transform.toString(transform),
    transition: transition || 'transform 300ms ease, box-shadow 300ms ease',
    padding: 16,
    margin: '0 0 10px 0',
    backgroundColor: '#ffffff',
    color: '#333',
    borderRadius: '6px',
    cursor: 'grab',
    boxShadow: isDragging
      ? '0 4px 12px rgba(30, 144, 255, 0.6)'
      : '0 2px 4px rgba(0,0,0,0.2)',
    userSelect: 'none',
    position: 'relative',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'flex-start',
    minHeight: '90px',
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <div style={{
        backgroundColor: priorityColors[priority] || '#888',
        width: '40px', height: '8px', borderRadius: '8px', position: 'absolute', top: 14, left: 16
      }} />
      {tags.length > 0 && (
        <div style={{ position: 'absolute', top: 8, right: 16, display: 'flex', gap: '6px' }}>
          {tags.map((tag, i) => (
            <span key={i} style={{ backgroundColor: '#e0e0e0', padding: '2px 8px', borderRadius: '12px', fontSize: '12px', color: '#333' }}>{tag}</span>
          ))}
        </div>
      )}
      <div style={{ marginTop: 25, marginBottom: 8, fontWeight: 600, fontSize: '15px', color: '#2c2c2c' }}>{content}</div>
      {dueDate && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '10px' }}>
          <span style={{ fontSize: '14px' }}>☰</span>
          <span style={{ backgroundColor: expired ? '#f8d7da' : '#f1f1f1', color: expired ? '#721c24' : '#333', borderRadius: '8px', padding: '4px 8px', fontSize: '12px', fontWeight: 'bold' }}>{countdown}</span>
        </div>
      )}
      {assignedUser && assignedTo.map((user, idx) => {
        const stringToColor = (str) => {
          let hash = 0;
          for (let i = 0; i < str.length; i++) {
            hash = str.charCodeAt(i) + ((hash << 5) - hash);
          }
          return `hsl(${hash % 360}, 70%, 60%)`;
        };

        const bgColor = stringToColor(user.username);

        return (
          <div key={user.id} title={`Asignado a: ${user.username}`} style={{
            position: 'absolute', bottom: 17, right: 15 + idx * 26,
            width: '24px', height: '24px', borderRadius: '50%',
            backgroundColor: bgColor, display: 'flex', alignItems: 'center',
            justifyContent: 'center', fontSize: '14px', fontWeight: 'bold',
            color: '#fff', textTransform: 'uppercase',
          }}>
            {user.username.charAt(0)}
          </div>
        );
      })}
    </div>
  );
}

function DroppableList({ id, listName, children }) {
  const { isOver, setNodeRef } = useDroppable({ id });
  return (
    <div ref={setNodeRef} style={{
      backgroundColor: isOver ? '#d0f0fd' : '#f0f0f0',
      padding: '16px', width: 260, minHeight: 250,
      borderRadius: 8,
      boxShadow: isOver ? '0 0 15px 3px #1e90ff' : '0 0 6px 1px rgba(0,0,0,0.1)'
    }}>
      <h3 style={{
        textTransform: 'capitalize', marginBottom: 16,
        marginLeft: 14, fontSize: '15px', fontWeight: 'bold', color: '#333'
      }}>{listName}</h3>
      {children}
    </div>
  );
}

export default function App() {
  const [userAuthenticated, setUserAuthenticated] = useState(null);
  const [user, setUser] = useState(null);
  const [boards, setBoards] = useState({});
  const sensors = useSensors(useSensor(PointerSensor));

  useEffect(() => {
    const token = localStorage.getItem('access');
    if (!token) return setUserAuthenticated(false);

    const headers = { Authorization: `Bearer ${token}` };

    axios.get(`${API_BASE_URL}/api/user/`, { headers })
      .then((res) => {
        setUser(res.data);
        setUserAuthenticated(true);
      })
      .catch(() => setUserAuthenticated(false));
  }, []);

  useEffect(() => {
    if (!userAuthenticated) return;
    const token = localStorage.getItem('access');
    axios.get(`${API_BASE_URL}/api/boards/`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        const data = {};
        res.data.forEach((board) => {
          const bid = `board${board.id}`;
          data[bid] = { name: board.name, lists: {} };
          board.task_lists.forEach((tl) => {
            const lid = `list${tl.id}`;
            data[bid].lists[lid] = {
              name: tl.name,
              tasks: tl.tasks
                .sort((a, b) => a.position - b.position)
                .map((task) => ({
                  id: `task-${task.id}`,
                  content: task.title,
                  priority: task.priority,
                  dueDate: task.due_date,
                  tags: Array.isArray(task.tags) ? task.tags : (task.tags || '').split(','),
                  assignedTo: task.assigned_to,
                })),
            };
          });
        });
        setBoards(data);
      })
      .catch(console.error);
  }, [userAuthenticated]);

  const handleLogout = () => {
    axios.post(`${API_BASE_URL}/logout/`)
      .then(() => {
        localStorage.removeItem('access');
        setUser(null);
        setUserAuthenticated(false);
      })
      .catch(console.error);
  };

  const handleDragEnd = async (event) => {
    const { active, over } = event;
    if (!active || !over || active.id === over.id) return;
    if (typeof over.id !== "string") return;

    const taskId = active.id;
    const taskIdNum = parseInt(taskId.replace("task-", ""), 10);

    let sourceListId = null;
    let destinationListId = null;
    let sourceBoardId = null;

    for (const [boardId, board] of Object.entries(boards)) {
      for (const [listId, list] of Object.entries(board.lists)) {
        if (list.tasks.some((task) => task.id === taskId)) {
          sourceListId = listId;
          sourceBoardId = boardId;
        }
      }
    }

    if (over.id.startsWith("list")) {
      destinationListId = over.id;
    } else if (over.data?.current?.sortable?.containerId) {
      destinationListId = over.data.current.sortable.containerId;
    }

    if (!sourceListId || !destinationListId || !sourceBoardId) return;
    if (sourceListId === destinationListId) return;

    const updatedBoards = { ...boards };
    const board = updatedBoards[sourceBoardId];
    if (!board) return;

    const sourceList = board.lists[sourceListId];
    const destinationList = board.lists[destinationListId];
    if (!sourceList || !destinationList) return;

    const movingTaskIndex = sourceList.tasks.findIndex((t) => t.id === taskId);
    if (movingTaskIndex === -1) return;

    const [movedTask] = sourceList.tasks.splice(movingTaskIndex, 1);
    destinationList.tasks.push(movedTask);

    // Recalcular las posiciones (índice) en la nueva lista
    destinationList.tasks.forEach((task, index) => {
      task.position = index;
    });

    setBoards(updatedBoards);

    // Obtener nueva posición y task_list ID
    const newTaskListId = parseInt(destinationListId.replace("list", ""), 10);
    const newPosition = destinationList.tasks.length - 1;

    try {
      await axios.patch(
        `${API_BASE_URL}/api/tasks/${taskIdNum}/`,
        {
          task_list: newTaskListId,
          position: newPosition
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access")}`,
          },
        }
      );
    } catch (error) {
      console.error("Error al actualizar la tarea en el backend:", error);
    }


  if (userAuthenticated === null) return <p>Cargando...</p>;

  const fetchUserData = () => {
    const token = localStorage.getItem('access');
    if (!token) return;

    axios.get(`${API_BASE_URL}/api/user/`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    .then(res => setUser(res.data))
    .catch(() => console.log("Error al obtener usuario"));
  };

  if (!userAuthenticated) return <LoginForm onLogin={() => {
    setUserAuthenticated(true);
    fetchUserData();
  }} />;

  return (
    <>
      <div style={{width: '1000px', margin: '0 auto', display: 'flex', flexDirection: 'column', alignItems: 'center'}} >
        <div style={{
          display: 'flex',
          justifyContent: 'flex-end',
          alignItems: 'center',
          gap: '12px',
          padding: '12px 20px',
          fontSize: '16px',
          fontFamily: 'sans-serif',
          marginTop: '40px',
          marginRight: '40px',
        }}>
          <span> Bienvenido  <strong>{user?.username}</strong></span>
          <span style={{ color: 'red', cursor: 'pointer', marginLeft: '8px' }} onClick={handleLogout}>
          | Cerrar sesión
        </span>
        </div>

        <div style={{ padding: '40px' }}>
          {Object.entries(boards).map(([boardId, board]) => (
            <div key={boardId} style={{ marginBottom: '60px' }}>
              <h2 style={{ marginBottom: '20px' }}>{board.name}</h2>
              <div style={{ display: 'flex', gap: '40px', justifyContent: 'center' }}>
                <DndContext sensors={sensors} collisionDetection={pointerWithin} onDragEnd={handleDragEnd}>
                  {Object.entries(board.lists).map(([listKey, listData]) => (
                    <DroppableList key={listKey} id={listKey} listName={listData.name}>
                      <SortableContext items={listData.tasks.map((t) => t.id)} strategy={verticalListSortingStrategy}>
                        {listData.tasks.map((task) => (
                          <SortableItem key={task.id} {...task} containerId={listKey} />
                        ))}
                      </SortableContext>
                    </DroppableList>
                  ))}
                </DndContext>
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
