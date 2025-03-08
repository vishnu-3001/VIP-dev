import { useState,useCallback } from "react";
import {fetchData} from "../Services/Documentservice";
export default function useGet(endpoint,data,config){
    const[data,setdata]=useState(data);
    const[error,seterror]=useState('');
    const[loading,setloading]=useState(false);
    const send=useCallback(async function send(data){
        setloading(true);
        seterror('');
        try{
            const resdata=await fetchData(endpoint,{...config,body:data});
            setdata(resdata);
        }catch(error){
            seterror(error);
        }
        setloading(false);
    },[endpoint,config]);
    return {
        data,
        error,
        loading,
        send
    }
}