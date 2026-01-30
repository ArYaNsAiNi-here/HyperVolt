'use client'

import React, { useRef, useState, useEffect, Suspense } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, useGLTF, Html } from '@react-three/drei'
import * as THREE from 'three'
import { motion, AnimatePresence } from 'framer-motion'
import { Loader2, AlertCircle, Home as HomeIcon } from 'lucide-react'

// --- Types ---
interface DigitalTwinProps {
  lightIntensity: number
  activeSource: 'solar' | 'battery' | 'grid'
  brightnessThreshold: number
  weatherCondition?: string
  className?: string
  onLoadingComplete?: (success: boolean) => void
}

type ModelLoadState = 'loading' | 'success' | 'error'

// --- 1. The Geometric Fallback House (No external files needed) ---
function GeometricHouse({
  lightIntensity,
  brightnessThreshold,
  needsArtificialLight,
  artificialLightIntensity
}: {
  lightIntensity: number
  brightnessThreshold: number
  needsArtificialLight: boolean
  artificialLightIntensity: number
}) {
  const groupRef = useRef<THREE.Group>(null)

  return (
    <group ref={groupRef} position={[0, -1, 0]}>
      {/* Base */}
      <mesh position={[0, 0.5, 0]} castShadow receiveShadow>
        <boxGeometry args={[4, 2, 4]} />
        <meshStandardMaterial color="#2D3748" />
      </mesh>
      {/* Roof */}
      <mesh position={[0, 2.0, 0]} castShadow>
        <coneGeometry args={[3.5, 1.5, 4]} />
        <meshStandardMaterial color="#1F2937"/>
      </mesh>
      {/* Door */}
      <mesh position={[0, 0.5, 2.01]}>
        <boxGeometry args={[0.8, 1.2, 0.1]} />
        <meshStandardMaterial color="#8B4513" />
      </mesh>
      {/* Windows */}
      <mesh position={[-1.2, 0.8, 2.01]}>
        <planeGeometry args={[0.8, 0.8]} />
        <meshStandardMaterial color={needsArtificialLight ? "#F6E05E" : "#4A5568"} emissive={needsArtificialLight ? "#F6E05E" : "#000000"} />
      </mesh>
      <mesh position={[1.2, 0.8, 2.01]}>
        <planeGeometry args={[0.8, 0.8]} />
        <meshStandardMaterial color={needsArtificialLight ? "#F6E05E" : "#4A5568"} emissive={needsArtificialLight ? "#F6E05E" : "#000000"} />
      </mesh>

      {/* Internal Light Logic */}
      {needsArtificialLight && (
        <pointLight
          position={[0, 1.5, 0]}
          intensity={artificialLightIntensity}
          color="#FFE5B4"
          distance={10}
          decay={2}
        />
      )}
    </group>
  )
}

// --- 2. The Real GLTF Model ---
function GLTFModel({ onLoad }: { onLoad: () => void }) {
  // This will SUSPEND if loading, or THROW if failed
    // during day
  const gltf = useGLTF('/models/tiny_isometric_room.glb')
    // during night
    // const gltf = useGLTF('/models/isometric_room_school.glb')

  // Report success once loaded
  useEffect(() => {
    onLoad()
  }, [onLoad])

  return (
    <primitive
      object={gltf.scene}
      position={[0, -1, 0]}
      scale={0.02} // Adjusted scale - if too small, increase this
    />
  )
}

// --- 3. Error Boundary to catch GLTF failures ---
class ModelErrorBoundary extends React.Component<
  { fallback: React.ReactNode; onError: () => void; children: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: any) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error: any) {
    console.error("3D Model Load Failed:", error)
    this.props.onError()
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback
    }
    return this.props.children
  }
}

// --- 4. Main Scene Component ---
function Scene({
  lightIntensity,
  brightnessThreshold,
  onLoadStateChange
}: {
  lightIntensity: number
  brightnessThreshold: number
  onLoadStateChange: (state: ModelLoadState) => void
}) {
  const needsArtificialLight = lightIntensity < brightnessThreshold
  const artificialLightIntensity = needsArtificialLight
    ? ((brightnessThreshold - lightIntensity) / 100) * 2
    : 0

  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={1} castShadow />
      <Environment />

      <ModelErrorBoundary
        onError={() => onLoadStateChange('error')}
        fallback={
          <GeometricHouse
            lightIntensity={lightIntensity}
            brightnessThreshold={brightnessThreshold}
            needsArtificialLight={needsArtificialLight}
            artificialLightIntensity={artificialLightIntensity}
          />
        }
      >
        <Suspense fallback={null}>
          <group>
            <GLTFModel onLoad={() => onLoadStateChange('success')} />
            {/* Add lights to the GLTF model specifically if needed */}
            {needsArtificialLight && (
              <pointLight
                position={[0, 5, 0]}
                intensity={artificialLightIntensity}
                color="#FFE5B4"
                distance={20}
                decay={2}
              />
            )}
          </group>
        </Suspense>
      </ModelErrorBoundary>
    </>
  )
}

// Helper for Environment (Sky/City reflection)
function Environment() {
  return (
    <mesh scale={100}>
      <sphereGeometry args={[1, 64, 64]} />
      <meshBasicMaterial color="#111" side={THREE.BackSide} />
    </mesh>
  )
}

// --- 5. Exported Component ---
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
    // Only update if state changes to prevent loops
    if (modelState !== state) {
      setModelState(state)
      setTimeout(() => {
        setShowContent(true)
        onLoadingComplete?.(state === 'success')
      }, 500)
    }
  }

  return (
    <div className={className} style={{ width: '100%', height: '100%', position: 'relative', overflow: 'hidden' }}>

      {/* Loading / Error Overlay */}
      <AnimatePresence>
        {!showContent && (
          <motion.div
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="absolute inset-0 z-10 flex items-center justify-center bg-gray-900 rounded-lg"
          >
            {modelState === 'loading' && (
              <div className="flex flex-col items-center gap-4">
                <Loader2 className="w-10 h-10 text-blue-500 animate-spin" />
                <p className="text-white font-medium">Loading Digital Twin...</p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Status Badge (Shows if using Fallback) */}
      {showContent && modelState === 'error' && (
        <div className="absolute top-4 left-4 z-10 bg-yellow-500/20 backdrop-blur-md border border-yellow-500/30 px-3 py-1.5 rounded-full flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-yellow-500" />
          <span className="text-xs text-yellow-200">Using Fallback Model</span>
        </div>
      )}

      {/* 3D Canvas */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: showContent ? 1 : 0 }}
        transition={{ duration: 1 }}
        style={{ width: '100%', height: '100%' }}
      >
        <Canvas shadows dpr={[1, 2]}>
          <PerspectiveCamera makeDefault position={[15, 10, 15]} fov={55} />
          <OrbitControls
            enablePan={false}
            minDistance={10}
            maxDistance={25}
            autoRotate
            autoRotateSpeed={0.5}
            target={[0, 0, 0]}
          />
          <Scene
            lightIntensity={lightIntensity}
            brightnessThreshold={brightnessThreshold}
            onLoadStateChange={handleLoadStateChange}
          />
        </Canvas>
      </motion.div>
    </div>
  )
}