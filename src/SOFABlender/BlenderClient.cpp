#include <sofa/component/visual/VisualModelImpl.h>
#include <sofa/core/ObjectFactory.h>
#include <SOFABlender/BlenderClient.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/core/visual/VisualModel.h>
#include <sofa/helper/ScopedAdvancedTimer.h>
#include <sofa/simulation/Node.h>
#include <SOFABlender/json/json.hpp>

namespace sofablender
{
int BlenderClientClass = sofa::core::RegisterObject("Client sending data to a Blender server")
    .add< BlenderClient >();

BlenderClient::BlenderClient()
    : d_host(initData(&d_host, std::string("127.0.0.1"), "host",
                      "Network address of the device running the server"))
    , d_port(initData(&d_port, 12345u, "port",
                      "Numeric value (ranging from 0 to 65535) identifying a communication channel with the server"))
    , m_socket(m_ioService)
{
    f_listening.setValue(true);
}

void BlenderClient::init()
{
    BaseObject::init();

    try
    {
        m_serverEndpoint = std::make_unique<boost::asio::ip::tcp::endpoint>(
            boost::asio::ip::address::from_string(d_host.getValue()), d_port.getValue());

        m_socket.connect(*m_serverEndpoint);
    }
    catch (std::exception& e)
    {
        msg_error() << "Initialization failed: " << e.what();
        this->d_componentState.setValue(sofa::core::objectmodel::ComponentState::Invalid);
        return;
    }

    sendData();
    ++m_nbIterations;

    this->d_componentState.setValue(sofa::core::objectmodel::ComponentState::Valid);
}

void BlenderClient::cleanup()
{
    BaseObject::cleanup();
    if (this->isComponentStateValid())
    {
        m_socket.close();
    }
}

void BlenderClient::handleEvent(sofa::core::objectmodel::Event* event)
{
    if (sofa::simulation::AnimateBeginEvent::checkEventType(event))
    {
        onBeginAnimationStep();
    }
}

void BlenderClient::sendHeader()
{
    std::stringstream header;
    header << "<SOFABlender>";

    boost::asio::write(m_socket, boost::asio::buffer(header.str()));
}

void BlenderClient::sendFooter()
{
    boost::asio::write(m_socket, boost::asio::buffer("</SOFABlender>"));
}

void BlenderClient::sendSerializedMeshes(const std::string& serializedMeshes)
{
    std::size_t pos = 0;
    static constexpr std::size_t chunkSize = 4096;
    while (pos < serializedMeshes.length())
    {
        const std::string chunk = serializedMeshes.substr(pos, chunkSize);
        boost::asio::write(m_socket, boost::asio::buffer(chunk));
        pos += chunkSize;
    }
}

void BlenderClient::convertMeshesToJSON(nlohmann::json& jsonMessage)
{
    auto* node = dynamic_cast<sofa::simulation::Node*>(this->getContext());
    if (!node)
    {
        msg_error() << "Not a Node";
        return;
    }

    jsonMessage["iteration"] = m_nbIterations;
    if (const auto& filename = this->getContext()->getRootContext()->getDefinitionSourceFileName(); !filename.empty())
    {
        jsonMessage["scene"] = filename;
    }

    toJson(node, jsonMessage);
}

void BlenderClient::toJson(sofa::simulation::Node* node, nlohmann::json& json)
{
    bool hasObjectsOrChildren = false;
    nlohmann::json jsonMeshes = nlohmann::json::array();
    for (const auto& object : node->object)
    {
        nlohmann::json jsonMesh;
        bool hasPosition = false;
        for (const auto& data : object->getDataFields())
        {
            const auto& name = data->getName();

            nlohmann::json faces = nlohmann::json::array();

            if (name == "position")
            {
                const auto typeInfo = data->getValueTypeInfo();
                if (typeInfo->Container() && !typeInfo->Text() && typeInfo->Scalar())
                {
                    hasPosition = true;

                    const sofa::Size nbDoFsByNode = typeInfo->size();
                    const sofa::Size nbElements = typeInfo->size(data->getValueVoidPtr()) / typeInfo->size();
                    nlohmann::json position = nlohmann::json::array();
                    for (unsigned int i = 0; i < nbElements; ++i)
                    {
                        nlohmann::json x = nlohmann::json::array();
                        for (sofa::Size j = 0; j < std::min(nbDoFsByNode, 3u); ++j)
                        {
                            x.push_back(typeInfo->getScalarValue(data->getValueVoidPtr(), i * nbDoFsByNode + j));
                        }
                        for (sofa::Size j = std::min(nbDoFsByNode, 3u); j < 3; ++j)
                        {
                            x.push_back(0);
                        }
                        position.push_back(x);
                    }
                    jsonMesh["position"] = position;
                }
            }
            else if (name == "faces" || name == "triangles" || name == "quads")
            {
                const auto typeInfo = data->getValueTypeInfo();
                if (typeInfo->Container() && !typeInfo->Text() && typeInfo->Integer())
                {
                    const sofa::Size nbVerticesByFace = typeInfo->size();
                    const sofa::Size nbFaces = typeInfo->size(data->getValueVoidPtr()) / typeInfo->size();

                    for (sofa::Size i = 0; i < nbFaces; ++i)
                    {
                        nlohmann::json f = nlohmann::json::array();
                        for (sofa::Size j = 0; j < nbVerticesByFace; ++j)
                        {
                            f.push_back(typeInfo->getIntegerValue(data->getValueVoidPtr(), i * nbVerticesByFace + j));
                        }
                        faces.push_back(f);
                    }
                }
            }
            if (!faces.empty())
            {
                jsonMesh["faces"] = faces;
            }
        }

        if (!jsonMesh.empty() && hasPosition)
        {
            jsonMesh["name"] = object->getName();
            jsonMeshes.push_back(jsonMesh);
        }
    }

    if (!jsonMeshes.empty())
    {
        json["objects"] = jsonMeshes;
        hasObjectsOrChildren = true;
    }

    const auto& children = node->getChildren();
    if (!children.empty())
    {
        nlohmann::json childJsonArray = nlohmann::json::array();
        for (const auto& child : children)
        {
            if (auto* childNode = dynamic_cast<sofa::simulation::Node*>(child))
            {
                nlohmann::json childJson;
                toJson(childNode, childJson);
                if (!childJson.empty())
                {
                    childJsonArray.push_back(childJson);
                }
            }
        }
        if (!childJsonArray.empty())
        {
            json["children"] = childJsonArray;
            hasObjectsOrChildren = true;
        }
    }

    if (hasObjectsOrChildren)
    {
        json["node_name"] = node->getName();
    }
}

void BlenderClient::sendData()
{
    if (!this->isComponentStateValid())
    {
        return;
    }

    SCOPED_TIMER("SendDataToBlender");

    sendHeader();
    {
        nlohmann::json jsonMessage;
        convertMeshesToJSON(jsonMessage);

        const auto jsonString = jsonMessage.dump();
        sendSerializedMeshes(jsonString);
    }
    sendFooter();
}

void BlenderClient::onBeginAnimationStep()
{
    sendData();
    ++m_nbIterations;
}


}
