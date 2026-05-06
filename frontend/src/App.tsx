import {
    BrowserRouter as Router,
    Route,
    Routes,
} from "react-router-dom";

import {LoginPage} from "./pages/LoginPage.tsx";
import {HomePage} from "./pages/HomePage.tsx";
import {NavBar} from "./components/NavBar.tsx";

function App() {
    return (
        <Router>
            <NavBar/>
            <Routes>
                <Route path="/" element={<HomePage/>}/>
                <Route path="/login" element={<LoginPage/>}/>
            </Routes>
        </Router>
    );
}

export default App;
