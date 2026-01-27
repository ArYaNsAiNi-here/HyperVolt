'use client'

import { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera } from '@react-three/drei'
import * as THREE from 'three'

interface DigitalTwinProps {
  lightIntensity: number // 0-100 from LDR sensor
  activeSource: 'solar' | 'battery' | 'grid'
  className?: string
}

function Room({ lightIntensity, activeSource }: { lightIntensity: number; activeSource: string }) {
  const roomRef = useRef<THREE.Group>(null)
  const lightRef = useRef<THREE.PointLight>(null)

  // Source colors
  const sourceColors = {
    solar: '#FDB022', // Yellow for solar
    battery: '#FF6B35', // Orange for battery
    grid: '#EF4444', // Red for grid
  }

  // Normalize light intensity (0-100) to (0.3-1.5) for visual effect
  const normalizedIntensity = 0.3 + (lightIntensity / 100) * 1.2

  useFrame((state) => {
    const time = state.clock.getElapsedTime()
    
    // Gentle pulsing effect based on active source
    if (roomRef.current) {
      const pulseFactor = Math.sin(time * 2) * 0.02 + 1
      roomRef.current.scale.set(pulseFactor, pulseFactor, pulseFactor)
    }

    // Update light intensity smoothly
    if (lightRef.current) {
      lightRef.current.intensity = normalizedIntensity + Math.sin(time) * 0.1
    }
  })

  // Floor color based on power source
  const floorColor = sourceColors[activeSource as keyof typeof sourceColors] || sourceColors.grid

  return (
    <group ref={roomRef}>
      {/* Room walls - wireframe style */}
      <lineSegments>
        <edgesGeometry args={[new THREE.BoxGeometry(5, 3, 5)]} />
        <lineBasicMaterial color="#4A5568" transparent opacity={0.6} />
      </lineSegments>

      {/* Floor with source color */}
      <mesh position={[0, -1.5, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[5, 5]} />
        <meshStandardMaterial 
          color={floorColor}
          transparent 
          opacity={0.2}
          emissive={floorColor}
          emissiveIntensity={0.3}
        />
      </mesh>

      {/* House representation in center */}
      <group position={[0, -0.8, 0]}>
        {/* House base */}
        <mesh position={[0, 0.4, 0]}>
          <boxGeometry args={[1.2, 0.8, 1.2]} />
          <meshStandardMaterial 
            color="#2D3748"
            emissive="#3B82F6"
            emissiveIntensity={0.2}
          />
        </mesh>
        {/* Roof */}
        <mesh position={[0, 1, 0]} rotation={[0, Math.PI / 4, 0]}>
          <coneGeometry args={[0.9, 0.6, 4]} />
          <meshStandardMaterial 
            color="#1F2937"
            emissive="#3B82F6"
            emissiveIntensity={0.1}
          />
        </mesh>
      </group>

      {/* Ceiling light representation */}
      <mesh position={[0, 1.3, 0]}>
        <sphereGeometry args={[0.15, 16, 16]} />
        <meshStandardMaterial 
          color="#FFF"
          emissive="#FFF"
          emissiveIntensity={normalizedIntensity * 2}
        />
      </mesh>

      {/* Light source */}
      <pointLight 
        ref={lightRef}
        position={[0, 1.3, 0]} 
        intensity={normalizedIntensity}
        color="#FFFFFF"
        distance={7}
        decay={2}
      />

      {/* Power Source Representations */}
      <PowerSources activeSource={activeSource} />

      {/* Energy particles flowing from source to house */}
      <EnergyParticles activeSource={activeSource} />

      {/* Ambient light for base visibility */}
      <ambientLight intensity={0.3} />
    </group>
  )
}

function EnergyParticles({ activeSource }: { activeSource: string }) {
  const particlesRef = useRef<THREE.Points>(null)

  const sourceColors = {
    solar: '#FDB022',
    battery: '#FF6B35',
    grid: '#EF4444',
  }

  // Source positions for particle animation
  const sourcePositions = {
    solar: { x: -2.5, y: 0.5, z: 2.5 },
    battery: { x: 2.5, y: -0.5, z: 2.5 },
    grid: { x: 0, y: 0, z: -2.8 },
  }

  // Create particles that flow from source to house
  const particles = useMemo(() => {
    const count = 40
    const positions = new Float32Array(count * 3)
    
    const sourcePos = sourcePositions[activeSource as keyof typeof sourcePositions] || sourcePositions.grid
    
    for (let i = 0; i < count; i++) {
      // Start particles near the active source
      const t = i / count
      positions[i * 3] = sourcePos.x * (1 - t) // x - move toward center
      positions[i * 3 + 1] = sourcePos.y * (1 - t) + (Math.random() - 0.5) * 0.3 // y
      positions[i * 3 + 2] = sourcePos.z * (1 - t) // z - move toward center
    }
    
    return positions
  }, [activeSource])

  useFrame((state) => {
    if (particlesRef.current) {
      const positions = particlesRef.current.geometry.attributes.position.array as Float32Array
      const sourcePos = sourcePositions[activeSource as keyof typeof sourcePositions] || sourcePositions.grid
      
      for (let i = 0; i < positions.length; i += 3) {
        // Move particles from source toward house (center)
        const dx = -positions[i] * 0.02
        const dy = -positions[i + 1] * 0.02
        const dz = -positions[i + 2] * 0.02
        
        positions[i] += dx
        positions[i + 1] += dy
        positions[i + 2] += dz
        
        // Reset particle to source position when it reaches center
        const distanceFromCenter = Math.sqrt(
          positions[i] * positions[i] + 
          positions[i + 1] * positions[i + 1] + 
          positions[i + 2] * positions[i + 2]
        )
        
        if (distanceFromCenter < 0.8) {
          positions[i] = sourcePos.x + (Math.random() - 0.5) * 0.3
          positions[i + 1] = sourcePos.y + (Math.random() - 0.5) * 0.3
          positions[i + 2] = sourcePos.z + (Math.random() - 0.5) * 0.3
        }
      }
      
      particlesRef.current.geometry.attributes.position.needsUpdate = true
    }
  })

  const particleColor = sourceColors[activeSource as keyof typeof sourceColors] || sourceColors.grid

  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particles.length / 3}
          array={particles}
          itemSize={3}
          args={[particles, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.08}
        color={particleColor}
        transparent
        opacity={0.8}
        sizeAttenuation
      />
    </points>
  )
}

function PowerSources({ activeSource }: { activeSource: string }) {
  const solarRef = useRef<THREE.Group>(null)
  const batteryRef = useRef<THREE.Group>(null)
  const gridRef = useRef<THREE.Group>(null)

  useFrame((state) => {
    const time = state.clock.getElapsedTime()
    
    // Pulse the active source
    if (activeSource === 'solar' && solarRef.current) {
      const scale = 1 + Math.sin(time * 3) * 0.1
      solarRef.current.scale.set(scale, scale, scale)
    }
    if (activeSource === 'battery' && batteryRef.current) {
      const scale = 1 + Math.sin(time * 3) * 0.1
      batteryRef.current.scale.set(scale, scale, scale)
    }
    if (activeSource === 'grid' && gridRef.current) {
      const scale = 1 + Math.sin(time * 3) * 0.1
      gridRef.current.scale.set(scale, scale, scale)
    }
  })

  return (
    <>
      {/* Solar Panel - Top Left */}
      <group ref={solarRef} position={[-2.5, 0.5, 2.5]}>
        {/* Panel surface */}
        <mesh rotation={[-Math.PI / 6, 0, 0]}>
          <boxGeometry args={[0.8, 0.05, 0.6]} />
          <meshStandardMaterial 
            color="#1E3A8A"
            emissive="#FDB022"
            emissiveIntensity={activeSource === 'solar' ? 0.6 : 0.1}
            metalness={0.8}
            roughness={0.2}
          />
        </mesh>
        {/* Panel stand */}
        <mesh position={[0, -0.3, 0]}>
          <cylinderGeometry args={[0.05, 0.05, 0.6]} />
          <meshStandardMaterial color="#374151" />
        </mesh>
        {/* Light indicator */}
        {activeSource === 'solar' && (
          <pointLight position={[0, 0.3, 0]} color="#FDB022" intensity={1} distance={3} />
        )}
      </group>

      {/* Battery - Top Right */}
      <group ref={batteryRef} position={[2.5, -0.5, 2.5]}>
        {/* Battery body */}
        <mesh>
          <cylinderGeometry args={[0.3, 0.3, 0.8]} />
          <meshStandardMaterial 
            color="#1F2937"
            emissive="#FF6B35"
            emissiveIntensity={activeSource === 'battery' ? 0.6 : 0.1}
            metalness={0.6}
            roughness={0.3}
          />
        </mesh>
        {/* Battery terminal */}
        <mesh position={[0, 0.5, 0]}>
          <cylinderGeometry args={[0.1, 0.1, 0.2]} />
          <meshStandardMaterial 
            color="#6B7280"
            emissive="#FF6B35"
            emissiveIntensity={activeSource === 'battery' ? 0.8 : 0.1}
          />
        </mesh>
        {/* Light indicator */}
        {activeSource === 'battery' && (
          <pointLight position={[0, 0.5, 0]} color="#FF6B35" intensity={1} distance={3} />
        )}
      </group>

      {/* Grid/Utility Pole - Back */}
      <group ref={gridRef} position={[0, 0, -2.8]}>
        {/* Pole */}
        <mesh>
          <cylinderGeometry args={[0.08, 0.08, 2]} />
          <meshStandardMaterial 
            color="#4B5563"
            emissive="#EF4444"
            emissiveIntensity={activeSource === 'grid' ? 0.4 : 0.05}
          />
        </mesh>
        {/* Cross beam */}
        <mesh position={[0, 0.8, 0]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.05, 0.05, 1.2]} />
          <meshStandardMaterial 
            color="#374151"
            emissive="#EF4444"
            emissiveIntensity={activeSource === 'grid' ? 0.5 : 0.05}
          />
        </mesh>
        {/* Power lines */}
        <mesh position={[-0.4, 0.8, 0]}>
          <cylinderGeometry args={[0.02, 0.02, 0.5]} />
          <meshStandardMaterial 
            color="#1F2937"
            emissive="#EF4444"
            emissiveIntensity={activeSource === 'grid' ? 0.7 : 0.1}
          />
        </mesh>
        <mesh position={[0.4, 0.8, 0]}>
          <cylinderGeometry args={[0.02, 0.02, 0.5]} />
          <meshStandardMaterial 
            color="#1F2937"
            emissive="#EF4444"
            emissiveIntensity={activeSource === 'grid' ? 0.7 : 0.1}
          />
        </mesh>
        {/* Light indicator */}
        {activeSource === 'grid' && (
          <pointLight position={[0, 1, 0]} color="#EF4444" intensity={1.2} distance={4} />
        )}
      </group>
    </>
  )
}

export default function DigitalTwin({ lightIntensity, activeSource, className }: DigitalTwinProps) {
  return (
    <div className={className} style={{ width: '100%', height: '100%' }}>
      <Canvas>
        <PerspectiveCamera makeDefault position={[4, 2, 4]} />
        <OrbitControls 
          enableZoom={true}
          enablePan={true}
          minDistance={3}
          maxDistance={15}
          autoRotate
          autoRotateSpeed={0.5}
        />
        <Room lightIntensity={lightIntensity} activeSource={activeSource} />
      </Canvas>
    </div>
  )
}
