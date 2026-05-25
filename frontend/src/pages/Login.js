import React from "react";
import '../styles/login.css'
import { useNavigate } from 'react-router-dom';


const Login = () => {

    const navigateTo = useNavigate();
    const [username, setUsername] = React.useState("");
    const [password, setPassword] = React.useState("");

    const loginUser = (e) => {
        
        e.preventDefault();
        const fetchUrl = "http://127.0.0.1:5000/api/login";

        fetch(fetchUrl, {
            method: "POST",
            headers: {
                "Content-type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        })
        .then(response => {
            if (!response.ok) {
                alert("Invalid login")
                throw new Error("Invalid login credentials");
            }

            return response.json();
        })
        .then(data => {
            console.log("Login Successful: ", data);
            localStorage.setItem("user", JSON.stringify(data.user_id));
            navigateTo("/home")
        })
        .catch(error => {
            console.error("Login error:", error);
        });
    }


    return (
        <div> 

            <div className="login-wrapper">
                <form className="login-form" onSubmit={loginUser}>
                    <h2> Login Below </h2>

                    <input
                        className="username-inpt"
                        type="text"
                        name="username"
                        value={username}
                        placeholder="Enter Username"
                        onChange = {(e) => setUsername(e.target.value)}
                    />

                    <input
                        className="password-input"
                        type="text"
                        name="password"
                        placeholder="Enter Password"
                        value={password}
                        onChange = {(e) => setPassword(e.target.value)}
                    />

                    <button type='submit'> Login </button>

                    <p> Don't have an account ? <a href='/register'> Sign up </a></p>
                </form>
            </div>
        </div>
    )
}


export default Login;