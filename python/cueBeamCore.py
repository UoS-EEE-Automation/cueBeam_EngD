import math
import numpy
import matplotlib.pyplot as plt


class CueBeamSolver:
    """ 
    This is the core of the cueBeam
    properties:
    * wavenumber(float) - the enviroment property
    * elements(list of TxElement) - description of the transmitters
    * rxPlane(single item of class RxPlane()) - describes the regular sampling plane
    
    """

    wavenumber = 1.0 / 1.0e-3  # wavelength = 1/wavenumber; so wavenumber = 1/wavelength
    "property of the environment: the wavenumber"

    class TxElement:
        x = 0.0
        y = 0.0
        z = 0.0
        amplitude = 1.0
        phase = 0.0

        def __init__(self, x=0.0, y=0.0, z=0.0, amplitude=1.0, phase=0.0):
            self.x = x
            self.y = y
            self.z = z
            self.amplitude = amplitude
            self.phase = phase

    elements = [TxElement(0.0, 0.0, -15.0e-3, 1.0, 0.0),
                TxElement(0.0, 0.0, -10.0e-3, 1.0, 0.0),
                TxElement(0.0, 0.0,  -5.0e-3, 1.0, 0.0),
                TxElement(0.0, 0.0,   0.0e-3, 1.0, 0.0),
                TxElement(0.0, 0.0,   5.0e-3, 1.0, 0.0),
                TxElement(0.0, 0.0,  10.0e-3, 1.0, 0.0),
                TxElement(0.0, 0.0,  15.0e-3, 1.0, 0.0)
                ]

    # for the planar sampling version:
    # the original Matlab version: img_xz = cueBeam_xz(tx',k,x0,y0,z0,nx,ny,nz,dx,dy,dz);
    class RxPlane:
        """describes a rectangular XZ section of the plane - and points of sampling(calculation) of the pressure"""
        x0 = -0.01e-3  # needs to be a little bit off plane to avoid division by zer
        y0 = -1.0e-3
        z0 = +0.0e-3
        dx = +1.0e-3
        dy = +1.0e-3
        dz = +1.0e-3
        nx = 1
        ny = 240
        nz = 160
        pressurefield = numpy.zeros((ny, nz), numpy.complex)

        def __init__(self, x0=-5.0e-3, y0=-5.0e-3, z0=0.0, dx=0.1e-3, dy=0.1e-3, dz=0.1e-3, nx=1, ny=10, nz=10):
            self.x0 = x0
            self.y0 = y0
            self.z0 = z0
            self.dx = dx
            self.dy = dy
            self.dz = dz
            if nx != 1:
                raise AttributeError("nx must be 1: ")
            if (ny > 4096) | (ny < 1):
                raise AttributeError("ny must have a sensible value between 1 an 4096")
            self.ny = ny
            if (nz > 4096) | (nz < 1):
                raise AttributeError("nz must have a sensible value between 1 and 4096")
            self.nz = nz
            self.clear_pressurefield()

        def verify_plane_endpoints(self):
            return [self.x0 + self.nx * self.dx, self.y0 + self.ny * self.dy, self.z0 + self.nz * self.dz]

        def clear_pressurefield(self):
            self.pressurefield = numpy.zeros((self.ny, self.nz), numpy.complex)

    rxPlane = RxPlane()

    def beamsim(self):

        # note: there is only a single plane implemented. This is for compatibility with the old Matlab-Cuda version.
        # Essentially, there should be no problem in extending this to 3D computation as needed.
        ix = 0
        for iz in range(self.rxPlane.nz):
            for iy in range(self.rxPlane.ny):
                pressure_re = 0.0
                pressure_im = 0.0
                pixel_x = self.rxPlane.x0 + ix * self.rxPlane.dx
                pixel_y = self.rxPlane.y0 + iy * self.rxPlane.dy
                pixel_z = self.rxPlane.z0 + iz * self.rxPlane.dz
                for itx in range(len(self.elements)):
                    ddx = (pixel_x - self.elements[itx].x)
                    ddy = (pixel_y - self.elements[itx].y)
                    ddz = (pixel_z - self.elements[itx].z)
                    distance = math.sqrt(ddx * ddx + ddy * ddy + ddz * ddz)
                    kphase = - self.wavenumber * distance + self.elements[itx].phase
                    kamplitude = self.elements[itx].amplitude / (2 * 3.14159 * distance)
                    pressure_re += math.cos(kphase) * kamplitude
                    pressure_im += math.sin(kphase) * kamplitude
                # mem write
                self.rxPlane.pressurefield[(iy, iz)] = pressure_re + 1.0j * pressure_im

                # end for iy
                # end for iz
                # end beamsim

    def do_plot(self):
        hfig = plt.figure(num=1, figsize=(8, 6), dpi=90, facecolor='white', edgecolor='black')
        imgplot = plt.imshow(
            X=numpy.real(self.rxPlane.pressurefield),
            extent=(
                self.rxPlane.z0, self.rxPlane.z0 + self.rxPlane.nz * self.rxPlane.dz,
                self.rxPlane.y0 + self.rxPlane.ny * self.rxPlane.dy, self.rxPlane.y0
            ),
            interpolation="spline36",
            clim=(-7.0, 7.0),
            origin="lower")
        plt.set_cmap("PRGn")
        plt.xlabel("z-axis[m]")
        plt.ylabel("y-axis[m]")
        plt.show()

        # q=cueBeamCore.CueBeamSolver()
        # q.rxPlane.clear_pressurefield()
        # q.beamsim()
