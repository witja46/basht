import os
import subprocess
from abc import ABC, abstractmethod

from ml_benchmark.config import Path


class ImageBuildWrapper(ABC):

    @abstractmethod
    def get_url(self):
        pass

    @abstractmethod
    def deploy_image(self, image, tag):
        pass

    @abstractmethod
    def cleanup(self,tag):
        pass


class MinikubeImageBuilder(ImageBuildWrapper):

    def __init__(self) -> None:
        pass

    def get_url(self):
        return subprocess.check_output("minikube ip", shell=True).decode("utf-8").strip("\n")

    def deploy_image(self, image, tag, build_context):
        call = subprocess.run(
            ["minikube", "image", "build", "-t", tag,  "-f", image, "."], cwd=build_context,
            capture_output=True)  # doesnt seem to work

        if call.returncode != 0:
            print(call.stderr.decode("utf-8").strip("\n"))
            raise Exception("Failed to deploy image")
        print("IMAGE IMAGE ", call.stdout, call.stderr)

        return call.stdout.decode("utf-8").strip("\n")

    def cleanup(self, tag):
        call = subprocess.run(["minikube","image", "rm",tag], shell=True, check=True)
        if call.returncode != 0:
            raise Exception("Failed to cleanup")

class DockerImageBuilder(ImageBuildWrapper):
    def __init__(self) -> None:
        pass

    def deploy_image(self, image, tag, build_context):
        call = subprocess.run(
            ["docker", "build", "-t", tag,  "-f", image, "."], cwd=build_context,
            capture_output=True)  # doesnt seem to work

        if call.returncode != 0:
            print(call.stderr.decode("utf-8").strip("\n"))
            raise Exception("Failed to build image")

        call = subprocess.run(
            ["docker", "push",tag] ,check=True)  # doesnt seem to work

        if call.returncode != 0:
            print(call.stderr.decode("utf-8").strip("\n"))
            raise Exception("Failed to deploy image")

        print("IMAGE IMAGE ", call.stdout, call.stderr)

        return call.stdout.decode("utf-8").strip("\n")

    def cleanup(self, tag):
        call = subprocess.run(
            ["docker", "image","rm",tag], check=True)  # doesnt seem to work
        if call.returncode != 0:
            raise Exception("Failed to cleanup")
