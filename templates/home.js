import React from 'react';
import { motion } from "framer-motion";

export default function Home() {
    return ( 
        <main className="min-h screen bg-gradient-to-br from green-50 via emerald-100 to blue-100 flex items-center justify-center p-6">
            <motion.div
                initial = {{opacity: 0, y: 50}}
                animate = {{opacity: 1, y:0}}
                transition = {{duration: 0.8}}
                className="bg-white rounded-3xl shadow-2xl p-10 max-w-5xl w-full grig grid-cols-1 md:grid-cols-2 gap-10"
        >
                <div className="space-y-6">
                    <h1 className="text-5xl font-extrabold text-emrald-700 leadong-tight">
                        Welcome to <span className="text-blue-600">PlantPulse</span>
                    </h1>
                    <p className="text-gray-700 text-lg">
                        Your all in one smart monitoring solution for plant health. Stay ahead of water needs, light exposure and temperature changes.
                    </p>
                    <a className="inline-block px-6 py-3 rounded-xl bg-to-r from emerald-500 to blue-500 text-white text-lg font-semibold shadow-lg hover:scale-105 transform transition duration-300 shadow-md"
                    >
                        Get Started
                    </a>
                </div>
                 
            <motion.div 
                 initial = {{opacity:0, scale:0.9}}
                 animate = {{opacity:1, scale:1}}
                 transition = {{delay:0.2, duratioin: 0.8}}
                 className="flex justify-center items-center"
                 >
                <img 
                    src="https://www.istockphoto.com/illustrations/green-plant-logo"
                    alt = "Plant Illustration"
                    className="w-full max-w-sm"
                    />
                </motion.div>
            </motion.div>
        </main>

    )
}