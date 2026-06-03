import React from "react";
import '../styles/login.css'
import { useNavigate } from 'react-router-dom';
import { useAuth } from "../AuthContext";


const Login = () => {

    const navigateTo = useNavigate();
    const [username, setUsername] = React.useState("");
    const [password, setPassword] = React.useState("");
    const [loading, setLoading] = React.useState(false);

    const {login} = useAuth();


    React.useEffect(() => {
        const loginbar = document.getElementById("login")

        if (loading) {
            loginbar.innerText = "Logging in ..."
        }
    }, [loading])

    const validateLogin = () => {

        let valid = true;

        const usernameMsg = document.getElementById("username");
        const passwordMsg = document.getElementById("password");

        usernameMsg.innerText = "";
        passwordMsg.innerText = "";
        
        if (!username.trim()) {
            usernameMsg.innerText = "⚠️ Error: Please type your username.**";
            valid = false
        }

        if (!password.trim()) {
            passwordMsg.innerText = "⚠️ Error: Please type your password.**";
            valid = false;
        }

        if (!valid) return false;

        return true;
    }

    const loginUser = async (e) => {
        e.preventDefault();

        if (!validateLogin()) return;

        const statusMsg = document.getElementById("username");
        statusMsg.innerText = "";

        const fetchUrl = "http://127.0.0.1:5000/api/login";

        try {
             
             
             const response = await fetch(fetchUrl, {
                method: "POST",
                headers: {
                    "Content-type": "application/json"
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            })

            
            const data = await response.json();

            if (!response.ok){
                statusMsg.innerText = "Invalid username or password. Try again.";
                return;
            }
            setLoading(true);
            
            login(data.token);
            navigateTo("/home");
            setLoading(false);

        } catch (error) {
            console.error("Login error: ", error);
            statusMsg.innerText = "Server error. Try again later.";
        }
     
    }


    return (
        <div> 

            <div className="login-wrapper">
                <form className="login-form" onSubmit={loginUser}>
                    <h2> Movie Recommender</h2>
                    <p className="login-subtitle"> Sign in to continue </p>

                    <p className="error" id="username"></p>
                    <input
                        className="username-inpt"
                        type="text"
                        name="username"
                        value={username}
                        placeholder="Enter Username"
                        onChange = {(e) => setUsername(e.target.value)}
                    />

                    <p className="error" id="password"></p>
                    <input
                        className="password-input"
                        type="text"
                        name="password"
                        placeholder="Enter Password"
                        value={password}
                        onChange = {(e) => setPassword(e.target.value)}
                    />

                    <button className="login-btn" type='submit' id="login"> Login </button>

                    <p> Don't have an account ? <a href='/register'> Sign up </a></p>
                </form>
            </div>
        </div>
    )
}


export default Login;