import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Viewer } from '@react-pdf-viewer/core';
import '@react-pdf-viewer/core/lib/styles/index.css';

export default function VoyeDashboard() {
    const [jsonData, setJsonData] = useState("{}");
    const [pdfUrl, setPdfUrl] = useState("");
    const [message, setMessage] = useState("Aucun message de traitement");

    return (
        <div className="flex flex-col h-screen">
            {/* Navigation Bar */}
            <div className="p-4 bg-gray-200 flex justify-between">
                <span className="font-bold">🏠 Navigation Bar</span>
                <div>
                    <Button className="mx-2">Menu 1</Button>
                    <Button>Menu 2</Button>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex flex-grow p-4 space-x-4">
                {/* JSON Viewer */}
                <Card className="flex-1">
                    <CardContent>
                        <h2 className="font-bold">📂 JSON Viewer</h2>
                        <Textarea
                            className="w-full h-96"
                            value={jsonData}
                            onChange={(e) => setJsonData(e.target.value)}
                        />
                    </CardContent>
                </Card>

                {/* PDF Viewer */}
                <Card className="flex-1">
                    <CardContent>
                        <h2 className="font-bold">📄 PDF Viewer</h2>
                        <Input
                            type="text"
                            placeholder="URL du PDF"
                            value={pdfUrl}
                            onChange={(e) => setPdfUrl(e.target.value)}
                        />
                        <div className="h-96 overflow-auto border mt-2">
                            {pdfUrl ? <Viewer fileUrl={pdfUrl} /> : <p>Aucun PDF chargé</p>}
                        </div>
                    </CardContent>
                </Card>

                {/* Validation */}
                <Card className="flex-1 flex flex-col items-center justify-center">
                    <CardContent>
                        <h2 className="font-bold">✅ Validation</h2>
                        <Button className="my-2" onClick={() => setMessage("Validation réussie")}>Bouton 1</Button>
                        <Button className="my-2" onClick={() => setMessage("Erreur détectée")}>Bouton 2</Button>
                    </CardContent>
                </Card>
            </div>

            {/* Message de traitement */}
            <div className="p-4 bg-gray-100 border-t">
                <span className="font-bold">🔔 Message de traitement :</span> {message}
            </div>
        </div>
    );
}
