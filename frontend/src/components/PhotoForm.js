// src/components/PhotoForm.js

import React, { useState, useRef } from 'react';

export default function PhotoForm({ onPhotoUpload }) {
    const [photo, setPhoto] = useState(null);
    const [error, setError] = useState(null);
    const [uploading, setUploading] = useState(false);
    const fileInputRef = useRef(null);

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const allowedTypes = ['image/jpeg', 'image/png'];
        if (!allowedTypes.includes(file.type)) {
            setError("Only PNG and JPG/JPEG files are allowed.");
        e.target.value = null; // reset file input
        setPhoto(null);
        return;
        }

        setPhoto(file);
        setError(null); 
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!photo) {
            setError("Please select a photo to upload");
            return;
        }

        const formData = new FormData();
        formData.append('photo', photo);

        try {
            setUploading(true);
            const res = await fetch('http://localhost:5000/upload', {
                method: 'POST',
                body: formData,
                credentials: 'include',
            });

            const data = await res.json();

            if (res.ok) {
                setError(null);
                setPhoto(null); // reset selected file
                fileInputRef.current.value = ''; // clear input
                if (onPhotoUpload) onPhotoUpload(data);
            } else {
                setError(data.error || "Upload failed");
            }
        } catch (err) {
            console.error(err);
            setError("Network error");
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="photo-form-container">
            <form onSubmit={handleSubmit} className="photo-form">
                <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    ref={fileInputRef}
                    required
                />
                {photo && <p>Selected file: {photo.name}</p>}
                <button type="submit" disabled={uploading}>
                    {uploading ? 'Uploading...' : 'Upload Photo'}
                </button>
            </form>
            {error && <p className="error-message">{error}</p>}
        </div>
    );
}
