'use client'

import { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, useGLTF } from '@react-three/drei'
import * as THREE from 'three'

interface DigitalTwinProps {
  lightIntensity: number
  activeSource: 'solar' | 'battery' | 'grid'
  brightnessThreshold: number
  weatherCondition?: string
  className?: string
}

function HouseModel({
  lightIntensity,
  brightnessThreshold,
  weatherCondition = 'sunny'
}: {
  lightIntensity: number
  brightnessThreshold: number
  weatherCondition: string
}) {
  const houseRef = useRef<THREE.Group>(null)

  // Load the GLTF model
  let gltf: any = null
  try {
    gltf = useGLTF('/models/sus_room.gltf')
  } catch (error) {
    console.log('GLTF model not found, using fallback')
  }

  const needsArtificialLight = lightIntensity < brightnessThreshold
  const artificialLightIntensity = needsArtificialLight
    ? ((brightnessThreshold - lightIntensity) / 100) * 1.5
    : 0

  useFrame((state) => {
    const time = state.clock.getElapsedTime()
    if (houseRef.current && gltf) {
      houseRef.current.rotation.y = Math.sin(time * 0.2) * 0.05
    }
  })

  if (gltf) {
    return (
      // FIX 1: Changed scale from 1 to 0.01 to convert cm to meters
      <group ref={houseRef} position={[0, -1, 0]} scale={0.01}>
        <primitive object={gltf.scene} />

        {needsArtificialLight && (
          <>
            {/* Adjusted light positions to match the new scale if necessary,
                but since they are children of the group, they might scale with it.
                If lights look tiny, move them OUTSIDE this group.
                For now, assuming lights should scale with the house. */}
            <pointLight
              position={[0, 200, 0]} // Scaled up position relative to group
              intensity={artificialLightIntensity}
              color="#FFE5B4"
              distance={600}
              decay={2}
            />
          </>
        )}
      </group>
    )
  }

  return (
    <group ref={houseRef} position={[0, 0, 0]}>
      {/* Fallback box model remains unchanged */}
      <mesh position={[0, 0.5, 0]}>
        <boxGeometry args={[2, 1, 2]} />
        <meshStandardMaterial color="#2D3748" />
      </mesh>
    </group>
  )
}

function Scene({ lightIntensity, brightnessThreshold, weatherCondition }: any) {
  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={1} castShadow />
      <HouseModel
        lightIntensity={lightIntensity}
        brightnessThreshold={brightnessThreshold}
        weatherCondition={weatherCondition}
      />
    </>
  )
}

export default function DigitalTwin({ lightIntensity, activeSource, brightnessThreshold, weatherCondition = 'sunny', className }: DigitalTwinProps) {
  return (
    <div className={className} style={{ width: '100%', height: '100%' }}>
      <Canvas shadows>
        {/* Camera is now effectively outside the 5 meter house */}
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
        />
      </Canvas>
    </div>
  )
}