import { useState } from 'react';
import '../styles/register.css'
import { useNavigate } from 'react-router-dom';
const Register = () => {

    const navigateTo = useNavigate();

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [checkPassword, setCheckPassword] = useState("");


    const checkMatch = () => password.trim() === checkPassword.trim();
    
    const validateRegisteration = () => {
        let valid = true;

        const usernameMsg = document.getElementById("username");
        const passwordMsg = document.getElementById("password");
        const secPasswordMsg = document.getElementById("password2")

        usernameMsg.innerText = "";
        passwordMsg.innerText = "";
        
        if (!username.trim()) {
            usernameMsg.innerText = "⚠️ Please type your username*";
            valid = false
        }

        if (!password.trim()) {
            passwordMsg.innerText = "⚠️ Please type your password*";
            valid = false;
        }

        if (!checkPassword.trim()) {
            secPasswordMsg.innerText = "⚠️ Please type your password again.*";
            valid = false;
        }

        if (!checkMatch()) {
            secPasswordMsg.innerText = "⚠️ Passwords must match*"
            valid = false
        }

        if (!valid) return false;

        return true;
    }

    const registerUser = (e) => {
        e.preventDefault();

        const isValid = validateRegisteration();

        if (!isValid) return;

        const fetchUrl = "http://127.0.0.1:5000/api/signup"

        fetch(fetchUrl, {
            method: "POST",
            headers: {
                "Content-type" : "application/json"
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        }).then(response => {
            if (!response.ok) {
                alert("Error signing up.")
                throw new Error("Unsuccessful Registration");
            }

            return response.json();
        }).then(response => {
            console.log("Registration successful: ", response);
            navigateTo("/");
        })
    }

    return (
        <div>
            <div className='register-wrapper'>
                <form className="register-form" onSubmit={registerUser}>
                    <h2> Register Below </h2>


                    <p className="error" id="username"></p>
                    <input
                        type="text"
                        name="username"
                        placeholder="Enter Username"
                        value={username}
                        onChange = {(e) => {setUsername(e.target.value)}} 
                    />

                    <p className="error" id="password"></p>
                    <input
                        type="text"
                        name="password"
                        placeholder="Enter Password"
                        value={password}
                        onChange = {(e) => {setPassword(e.target.value)}}
                    />

                    <p className="error" id="password2"></p>
                    <input
                        type="text"
                        name="password"
                        placeholder="Enter Password Again"
                        value={checkPassword}
                        onChange = {(e) => {setCheckPassword(e.target.value)}}
                    />

                    <button type="submit"> Register </button>

                    <p> Already have an account ? <a href='/'> Login </a></p>
                </form>
            </div>
        </div>
    )
}

export default Register;