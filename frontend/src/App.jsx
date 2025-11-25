import { useState } from 'react'
import heic2any from "heic2any"

function App() {
  const [selectedImage, setSelectedImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [classification, setClassification] = useState(null)
  const [isClassifying, setIsClassifying] = useState(false)

  const API_URL = `${import.meta.env.VITE_API_URL}/api/classify`;

  const handleImageSelect = async (event) => {
    const file = event.target.files[0]
    if (file) {
      setSelectedImage(file)
      setClassification(null)

      // HEIC Conversion
      if (file.type === "image/heic" || file.name.endsWith(".heic")) {
        try {
          const convertedBlob = await heic2any({
            blob: file,
            toType: "image/jpeg",
          })

          const convertedImage = new File(
            [convertedBlob],
            file.name.replace(".heic", ".jpg"),
            { type: "image/jpeg" }
          )

          setSelectedImage(convertedImage)

          const reader = new FileReader()
          reader.onloadend = () => setImagePreview(reader.result)
          reader.readAsDataURL(convertedImage)
          return
        } catch (error) {
          console.error("Image conversion failed:", error)
        }
      }

      const reader = new FileReader()
      reader.onloadend = () => setImagePreview(reader.result)
      reader.readAsDataURL(file)
    }
  }

  const handleClassify = async () => {
    if (!selectedImage) return

    setIsClassifying(true)
    const formData = new FormData()
    formData.append("image", selectedImage)

    try {
      const response = await fetch(`${API_URL}`, {
        method: "POST",
        body: formData,
      })
      const result = await response.json()
      setClassification(result)
    } catch (error) {
      console.error("Error:", error)
    }
    setIsClassifying(false)
  }

  const handleReset = () => {
    setSelectedImage(null)
    setImagePreview(null)
    setClassification(null)
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-6">
      <div className="w-full max-w-xl bg-white shadow-xl rounded-2xl p-8 space-y-6 border border-gray-200">

        {/* Title */}
        <h1 className="text-3xl font-bold text-center text-gray-900">
          Waste Classifier
        </h1>
        <p className="text-center text-gray-500 -mt-2">
          Upload an image to classify waste type
        </p>

        {/* Upload Section */}
        <div className="flex flex-col items-center">
          <input
            type="file"
            accept="image/*"
            onChange={handleImageSelect}
            className="hidden"
            id="upload"
          />

          <label
            htmlFor="upload"
            className="w-full max-w-xs border-2 border-gray-300 text-gray-700 rounded-xl px-6 py-4 text-center cursor-pointer hover:bg-gray-50 hover:border-gray-400 transition-all font-medium"
          >
            Select Image
          </label>

          {imagePreview && (
            <img
              src={imagePreview}
              alt="preview"
              className="mt-4 w-full h-64 object-contain rounded-xl bg-gray-50 border border-gray-200"
            />
          )}
        </div>

        {/* Classify Button */}
        {imagePreview && (
          <button
            onClick={handleClassify}
            disabled={isClassifying}
            className="w-full px-10 py-3 rounded-lg text-lg font-semibold 
            bg-green-700 text-white 
            hover:bg-green-800 
            disabled:bg-green-200 disabled:text-gray-100 
            transition-all">
            {isClassifying ? "Classifying..." : "Classify Waste"}
          </button>
        )}

        {/* Results */}
        {classification && (
          <div className="bg-gray-50 border border-gray-300 rounded-xl p-6 space-y-2">
            <h2 className="text-xl font-semibold text-gray-800 text-center">
              Result
            </h2>

            <div className="text-center">
              <span className="text-3xl font-bold text-gray-900">
                {classification.category}
              </span>
            </div>

            {/* Reset */}
            <div className="flex justify-center pt-3">
              <button
                onClick={handleReset}
                className="px-6 py-2 rounded-lg font-semibold
                  border-2 border-red-600 text-red-600
                  hover:bg-red-600 hover:text-white transition"
              >
                Reset
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
