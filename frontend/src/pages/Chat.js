import React from 'react'
import '../styles/chat.css'
import { useAuth } from '../AuthContext'

const Chat = () => {

    const {authFetch} = useAuth();

    const bottomRef = React.useRef();

    // This component will be dedicated to building a mini chatbot message page
    // with an ai agent specialized for this app, and trained only on the knowledge of the 
    // database.

    // All chat messages will be stored in an array where the sender is tracked between "user" and "bot".
    const [messages, setMessages] = React.useState([
        {
            sender: "bot",
            text: "Hello, I am your personal assistant!"
        }
    ])

    const [input, setInput] = React.useState("");

    // whenever messages change, auto scroll to newest message.
    React.useEffect(() => {
        bottomRef.current?.scrollIntoView({
            behavior: "smooth"
        });
    }, [messages])

    const sendMessage = async (e) => {
        e.preventDefault();

        // USER'S INPUT

        if (!input.trim()) return;

        setMessages(prev => [
            ...prev , {
                sender: "user",
                text: input
            }
        ]);

        // capture input for AI bot before we reset.
        const userInput = input;

        setInput("");


        // CHATBOT REPSONSE

        try {
            const response = await authFetch("http://localhost:5000/api/chatbot", {
                method: "POST",
                headers: {
                    "Content-Type" : "application/json"
                },
                body: JSON.stringify({
                    message: userInput
                })
            })

            const chatAnswer = await response.json();

            setMessages(prev => [
                ...prev, 
                {
                    sender: "bot",
                    text: chatAnswer.reply
                }
            ])

        } catch (error) {
            setMessages(prev => [
                ...prev, 
                {
                    sender: "bot",
                    text: "Sorry, something went wrong."
                }
            ])
        }
    }

    return (
        <>
        <div className='chat-container' ref={bottomRef}>
            <div className="chat-window">
                {/* Rendering the conversation*/}
                {messages.map((message, index) => (

                    <div 
                        key={index}
                        className={
                            message.sender === "user" ? "user-message" : "bot-message"
                        }
                    >
                        {message.text}
                    </div>
                ))}
            </div>

            <form className="chat-input-form">

                <input
                    className="chat-input"
                    placeholder="Ask MidnightScoop about movies..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                />

                <button className="chat-send-btn" onClick={(e) => sendMessage(e)}>
                    Send
                </button>

            </form>

        </div>
        
        </>

    )
}

export default Chat;
