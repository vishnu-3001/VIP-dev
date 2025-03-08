import { useActionState } from "react";
export default function DocumentFetch(){
    function fetchDocument(prevStatus,fd){
        const formData=Object.fromEntries(fd.entries());
        console.log(formData);
    }
    const[formstatus,formAction,pending]=useActionState(fetchDocument)
    return(
        <div>
            <form action={formAction}>
                <label>Enter the google document link here link here</label>
                <input name="form-link" id="form-link"></input>
                <button>Fetch Document</button>
            </form>
        </div>
    )
}