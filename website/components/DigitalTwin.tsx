'use client'

import { useRef, useState, useEffect } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, useGLTF } from '@react-three/drei'
import * as THREE from 'three'
import { motion, AnimatePresence } from 'framer-motion'
import { Loader2, AlertCircle, Home as HomeIcon } from 'lucide-react'

interface DigitalTwinProps {
  lightIntensity: number
  activeSource: 'solar' | 'battery' | 'grid'
  brightnessThreshold: number
  weatherCondition?: string
  className?: string
  onLoadingComplete?: (success: boolean) => void
}

type ModelLoadState = 'loading' | 'success' | 'error'

function HouseModel({
  lightIntensity,
  brightnessThreshold,
  weatherCondition = 'sunny',
  onLoadStateChange,
}: {
  lightIntensity: number
  brightnessThreshold: number
  weatherCondition: string
  onLoadStateChange?: (state: ModelLoadState) => void
}) {
  const houseRef = useRef<THREE.Group>(null)
  const [loadState, setLoadState] = useState<ModelLoadState>('loading')

  // Load the GLTF model with error handling
  let gltf: any = null
  let loadError = false
  
  try {
    gltf = useGLTF('/models/sus_room.gltf')
    
    // Check if model loaded successfully
    useEffect(() => {
      if (gltf && gltf.scene) {
        setLoadState('success')
        onLoadStateChange?.('success')
      }
    }, [gltf])
  } catch (error) {
    console.error('GLTF model loading failed:', error)
    loadError = true
    
    useEffect(() => {
      setLoadState('error')
      onLoadStateChange?.('error')
    }, [])
  }

  const needsArtificialLight = lightIntensity < brightnessThreshold
  const artificialLightIntensity = needsArtificialLight
    ? ((brightnessThreshold - lightIntensity) / 100) * 1.5
    : 0

  useFrame((state) => {
    const time = state.clock.getElapsedTime()
    if (houseRef.current) {
      houseRef.current.rotation.y = Math.sin(time * 0.2) * 0.05
    }
  })

  // If model loaded successfully, render it
  if (gltf && !loadError) {
    return (
      <group ref={houseRef} position={[0, -1, 0]} scale={0.01}>
        <primitive object={gltf.scene} />

        {needsArtificialLight && (
          <pointLight
            position={[0, 200, 0]}
            intensity={artificialLightIntensity}
            color="#FFE5B4"
            distance={600}
            decay={2}
          />
        )}
      </group>
    )
  }

  // Fallback model
  return (
    <group ref={houseRef} position={[0, 0, 0]}>
      {/* Simple house representation */}
      <mesh position={[0, 0.5, 0]} castShadow>
        <boxGeometry args={[2, 1, 2]} />
        <meshStandardMaterial color="#2D3748" />
      </mesh>
      {/* Roof */}
      <mesh position={[0, 1.3, 0]} castShadow>
        <coneGeometry args={[1.5, 0.8, 4]} />
        <meshStandardMaterial color="#1F2937" />
      </mesh>
      {/* Door */}
      <mesh position={[0, 0.3, 1.01]}>
        <boxGeometry args={[0.4, 0.6, 0.05]} />
        <meshStandardMaterial color="#8B4513" />
      </mesh>
      {needsArtificialLight && (
        <pointLight
          position={[0, 1.5, 0]}
          intensity={artificialLightIntensity}
          color="#FFE5B4"
          distance={6}
          decay={2}
        />
      )}
    </group>
  )
}

function Scene({ lightIntensity, brightnessThreshold, weatherCondition, onLoadStateChange }: any) {
  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={1} castShadow />
      <HouseModel
        lightIntensity={lightIntensity}
        brightnessThreshold={brightnessThreshold}
        weatherCondition={weatherCondition}
        onLoadStateChange={onLoadStateChange}
      />
    </>
  )
}

export default function DigitalTwin({ 
  lightIntensity, 
  activeSource, 
  brightnessThreshold, 
  weatherCondition = 'sunny', 
  className,
  onLoadingComplete 
}: DigitalTwinProps) {
  const [modelState, setModelState] = useState<ModelLoadState>('loading')
  const [showContent, setShowContent] = useState(false)

  const handleLoadStateChange = (state: ModelLoadState) => {
    setModelState(state)
    // Add a small delay before showing content for smooth transition
    setTimeout(() => {
      setShowContent(true)
      onLoadingComplete?.(state === 'success')
    }, 500)
  }

  return (
    <div className={className} style={{ width: '100%', height: '100%', position: 'relative' }}>
      {/* Loading/Error Overlay */}
      <AnimatePresence>
        {!showContent && (
          <motion.div
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="absolute inset-0 z-10 flex items-center justify-center bg-gray-900/95 rounded-lg"
          >
            {modelState === 'loading' && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex flex-col items-center gap-4"
              >
                <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
                <div className="text-center">
                  <p className="text-white font-semibold">Loading 3D Model</p>
                  <p className="text-gray-400 text-sm mt-1">Please wait...</p>
                </div>
              </motion.div>
            )}
            {modelState === 'error' && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex flex-col items-center gap-4"
              >
                <div className="p-3 bg-yellow-500/20 rounded-full">
                  <HomeIcon className="w-12 h-12 text-yellow-500" />
                </div>
                <div className="text-center">
                  <p className="text-white font-semibold">Using Fallback Model</p>
                  <p className="text-gray-400 text-sm mt-1">3D model unavailable</p>
                </div>
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* 3D Canvas */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: showContent ? 1 : 0 }}
        transition={{ duration: 0.5 }}
        style={{ width: '100%', height: '100%' }}
      >
        <Canvas shadows>
          <PerspectiveCamera makeDefault position={[8, 5, 8]} />
          <OrbitControls
            enableZoom={true}
            enablePan={true}
            minDistance={2}
            maxDistance={20}
            autoRotate
            autoRotateSpeed={0.8}
          />
          <Scene
            lightIntensity={lightIntensity}
            brightnessThreshold={brightnessThreshold}
            weatherCondition={weatherCondition}
            onLoadStateChange={handleLoadStateChange}
          />
        </Canvas>
      </motion.div>
    </div>
  )
}