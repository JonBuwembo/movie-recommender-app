import React from 'react'
import '../styles/chat.css'
import { useAuth } from '../AuthContext'
import Navbar from '../components/Navbar/Navbar';
import '../components/Navbar/Navbar.css';


const ChatStartSceen = () => {

    const [input, setInput] = React.useState("");
    const [isloading, setIsLoading] = React.useState(false);
    const [response, setResponse] = React.useState("");
    const {authFetch} = useAuth();

    // This component will be dedicated to building a mini chatbot message page
    // with an ai agent specialized for this app, and trained only on the knowledge of the 
    // database.

    // All chat messages will be stored in an array where the sender is tracked between "user" and "bot".

    const sendMessage = async (e) => {
        e.preventDefault()

        if (!input || !input.trim()) return;

        // USER'S INPUT

        if (!input.trim()) return;
        setIsLoading(true);

        setInput(input);

        // capture input for AI bot before we reset.
        const userInput = input;

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

            setResponse(chatAnswer.reply);
            setIsLoading(false);

        } catch (error) {
            setResponse("Sorry, something went wrong.");
            console.error("Error: ", error)
        }
    }

    return (
    <>
        <Navbar />
        <div className="chat-screen">

            <div className='top-message'>
                <h1> How can I help you? </h1>
                <p> Tell me your vibe. I’ll pick the movie.</p>
            </div>
            

            <form onSubmit={sendMessage}>
                <input 
                    className="chat-input"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder='Ask me something...'
                 />
            </form>

            {isloading? (
                <div className="loading-bars"> 
                    <div />
                    <div />
                    <div />
                    <div />
                    <div />
                    <div />
                </div>
                
            ) : response && (
                <div className='bot-response'>
                    {response}
                </div>
            )}

        </div>
    </>
    )
}

export default ChatStartSceen;